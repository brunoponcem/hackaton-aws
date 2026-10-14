from datetime import date, datetime

import pytest

from src.agent.cli import demo_case
from src.agent.loop import LIMIT_REPLY, Agent, history_to_converse
from src.agent.route import build_route
from src.agent.tools import build_registry
from src.contracts import (
    Case,
    Channel,
    ChecklistStatus,
    Message,
    MessageRole,
    Milestone,
    MilestoneKind,
    PguResult,
    PguStatus,
    Reason,
    Requirement,
)

RUN = "100000001-5"
REF = date(2026, 10, 8)
NOW = datetime(2026, 10, 14, 12, 0)
OPENS = date(2027, 7, 1)


class ScriptedClient:
    """Fake Converse client: returns queued responses and records each request."""

    def __init__(self, responses):
        self.responses = list(responses)
        self.requests = []

    def converse(self, messages, **options):
        self.requests.append({"messages": [dict(m) for m in messages], **options})
        return self.responses.pop(0)


def tool_use(name, tool_input=None, tool_id="t1"):
    content = [{"toolUse": {"toolUseId": tool_id, "name": name, "input": tool_input or {}}}]
    return {
        "output": {"message": {"role": "assistant", "content": content}},
        "stopReason": "tool_use",
    }


def answer(text):
    return {
        "output": {"message": {"role": "assistant", "content": [{"text": text}]}},
        "stopReason": "end_turn",
    }


def fake_pgu(profile, reference_date):
    return PguResult(run=profile.run, status=PguStatus.UPCOMING, reference_date=reference_date)


def fake_milestones(profile, reference_date):
    return [
        Milestone(
            kind=MilestoneKind.PGU_APPLICATION_OPENS,
            date=OPENS,
            description="Apertura de la solicitud PGU",
        )
    ]


def registry(**kwargs):
    return build_registry(load_default_rules=False, **kwargs)


def tool_results(client, request_index):
    return [
        block["toolResult"]
        for block in client.requests[request_index]["messages"][-1]["content"]
        if "toolResult" in block
    ]


def test_tool_call_then_answer_updates_case():
    case = demo_case(RUN, Channel.WEB, NOW)
    client = ScriptedClient(
        [tool_use("consultar_perfil", {"run": "100.000.001-5"}), answer("Listo")]
    )
    reply = Agent(client, registry(), REF).run_turn(case, "Hola", now=NOW)

    assert reply.text == "Listo"
    assert [(c.name, c.ok) for c in reply.tool_calls] == [("consultar_perfil", True)]
    result = tool_results(client, 1)[0]
    assert result["status"] == "success"
    assert result["content"][0]["json"]["data"]["profile"]["run"] == RUN
    assert [m.role for m in case.messages] == [MessageRole.PERSON, MessageRole.AGENT]


def test_unauthorized_profile_is_an_error_result_not_a_crash():
    case = Case(case_id="c", run=RUN, created_at=NOW)
    client = ScriptedClient(
        [tool_use("consultar_perfil", {"run": RUN}), answer("Necesito tu permiso")]
    )
    reply = Agent(client, registry(), REF).run_turn(case, "Hola", now=NOW)

    result = tool_results(client, 1)[0]
    assert result["status"] == "error"
    assert result["content"][0]["json"]["error"]["type"] == "permission_denied"
    assert reply.tool_calls[0].ok is False


def test_other_persons_run_is_rejected():
    case = demo_case(RUN, Channel.WEB, NOW)
    client = ScriptedClient([tool_use("consultar_perfil", {"run": "100000002-3"}), answer("No")])
    Agent(client, registry(), REF).run_turn(case, "Hola", now=NOW)
    assert tool_results(client, 1)[0]["content"][0]["json"]["error"]["type"] == "permission_denied"


def test_unknown_tool_returns_error():
    case = demo_case(RUN, Channel.WEB, NOW)
    client = ScriptedClient([tool_use("inventar_beneficio"), answer("Ok")])
    Agent(client, registry(), REF).run_turn(case, "Hola", now=NOW)
    assert tool_results(client, 1)[0]["content"][0]["json"]["error"]["type"] == "unknown_tool"


def test_iteration_limit_stops_the_loop():
    case = demo_case(RUN, Channel.WEB, NOW)
    client = ScriptedClient([tool_use("leer_caso", tool_id=f"t{i}") for i in range(3)])
    reply = Agent(client, registry(), REF, max_iterations=3).run_turn(case, "Hola", now=NOW)
    assert reply.hit_iteration_limit is True
    assert reply.text == LIMIT_REPLY
    assert case.messages[-1].text == LIMIT_REPLY


def test_only_implemented_tools_are_offered():
    case = demo_case(RUN, Channel.WEB, NOW)
    client = ScriptedClient([answer("Hola")])
    Agent(client, registry(), REF).run_turn(case, "Hola", now=NOW)
    names = [t["toolSpec"]["name"] for t in client.requests[0]["toolConfig"]["tools"]]
    assert names == ["consultar_perfil", "leer_caso"]


def test_rules_fill_result_milestones_route_and_checklist():
    case = demo_case(RUN, Channel.WEB, NOW)
    client = ScriptedClient(
        [
            tool_use("calcular_hitos", tool_id="a"),
            tool_use("evaluar_pgu", tool_id="b"),
            answer("Ruta"),
        ]
    )
    tools = registry(pgu_rule=fake_pgu, milestones_rule=fake_milestones)
    Agent(client, tools, REF).run_turn(case, "Hola", now=NOW)

    assert case.pgu_result.status == PguStatus.UPCOMING
    assert case.pgu_result.reference_date == REF
    assert case.milestones[0].date == OPENS
    assert any(step.available_from == OPENS for step in case.route)
    assert {item.item_id for item in case.checklist} == {"rsh", "solicitud"}
    assert all(item.status == ChecklistStatus.PENDING for item in case.checklist)


def test_system_prompt_carries_trusted_case_context():
    case = demo_case(RUN, Channel.BRANCH, NOW)
    client = ScriptedClient([answer("Hola")])
    Agent(client, registry(), REF).run_turn(case, "Hola", channel=Channel.BRANCH, now=NOW)
    context = client.requests[0]["system"][1]["text"]
    assert "Canal actual: sucursal" in context
    assert "Acceso al perfil autorizado: sí" in context
    assert REF.isoformat() in context


def test_history_marks_other_channels_and_alternates():
    messages = [
        Message(role=MessageRole.AGENT, channel=Channel.WEB, text="Bienvenida", created_at=NOW),
        Message(role=MessageRole.PERSON, channel=Channel.WEB, text="Hola", created_at=NOW),
        Message(role=MessageRole.OFFICER, channel=Channel.BRANCH, text="Revisé", created_at=NOW),
    ]
    turns = history_to_converse(messages, Channel.BRANCH)
    assert [t["role"] for t in turns] == ["user", "assistant", "user"]
    assert turns[2]["content"][0]["text"] == "[persona · web] Hola"
    assert turns[2]["content"][1]["text"] == "[ejecutivo · sucursal] Revisé"


@pytest.mark.parametrize(
    ("requirement", "item_id"), [(Requirement.PFP, "rsh"), (Requirement.RESIDENCE, "residencia")]
)
def test_missing_records_become_steps(requirement, item_id):
    result = PguResult(
        run=RUN,
        status=PguStatus.MISSING_RECORD,
        reference_date=REF,
        reasons=[Reason(requirement=requirement, met=None, message="Sin registro")],
    )
    route, checklist = build_route(result, [])
    assert [i.item_id for i in checklist] == [item_id]
    assert route[-1].title == "Vuelve a pedir tu orientación"
    assert all(step.source and not step.source.verified for step in route)
