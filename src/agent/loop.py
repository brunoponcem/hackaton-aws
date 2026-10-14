"""Agent turn with Bedrock Converse + tool use (T04, ADR 0003)."""

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Any, Protocol

from src.agent.prompts import SYSTEM_PROMPT, build_tool_config
from src.agent.tools import ToolContext, ToolRegistry
from src.contracts import Case, Channel, Message, MessageRole

LIMIT_REPLY = (
    "No pude completar tu orientación en este momento. Tu caso quedó guardado; "
    "puedes intentarlo de nuevo o continuar con un ejecutivo."
)


class ConverseClient(Protocol):
    def converse(self, messages: list[dict[str, Any]], **options: Any) -> dict[str, Any]: ...


@dataclass
class ToolCall:
    name: str
    ok: bool


@dataclass
class AgentReply:
    text: str
    tool_calls: list[ToolCall] = field(default_factory=list)
    hit_iteration_limit: bool = False


def case_context(case: Case, channel: Channel, reference_date: date) -> str:
    """Trusted facts from the application, appended to the system prompt each turn."""
    invitation = case.invitation.response.value if case.invitation else "sin invitación"
    authorized = "sí" if case.can_read_profile else "no"
    previous = case.pgu_result.status.value if case.pgu_result else "ninguna"
    lines = [
        "Contexto del caso entregado por la aplicación (no por la persona):",
        f"- Canal actual: {channel.value}",
        f"- Fecha de referencia para evaluar: {reference_date.isoformat()}",
        f"- RUN del caso: {case.run}",
        f"- Invitación: {invitation}",
        f"- Acceso al perfil autorizado: {authorized}",
        f"- Evaluación PGU previa: {previous}",
    ]
    return "\n".join(lines)


def history_to_converse(messages: list[Message], current: Channel) -> list[dict[str, Any]]:
    """Map case messages to alternating Converse turns, starting with the user."""
    turns: list[dict[str, Any]] = []
    for message in messages:
        role = "assistant" if message.role == MessageRole.AGENT else "user"
        text = message.text
        if role == "user" and (message.role != MessageRole.PERSON or message.channel != current):
            text = f"[{message.role.value} · {message.channel.value}] {text}"
        if turns and turns[-1]["role"] == role:
            turns[-1]["content"].append({"text": text})
        else:
            turns.append({"role": role, "content": [{"text": text}]})
    if turns and turns[0]["role"] == "assistant":
        turns.insert(0, {"role": "user", "content": [{"text": "[sistema] Inicio del caso."}]})
    return turns


@dataclass
class Agent:
    client: ConverseClient
    tools: ToolRegistry
    reference_date: date
    max_iterations: int = 6
    max_tokens: int = 1500

    def run_turn(
        self,
        case: Case,
        text: str,
        *,
        channel: Channel = Channel.WEB,
        role: MessageRole = MessageRole.PERSON,
        now: datetime | None = None,
    ) -> AgentReply:
        now = now or datetime.now()
        case.messages.append(Message(role=role, channel=channel, text=text, created_at=now))
        messages = history_to_converse(case.messages, channel)
        system = [
            {"text": SYSTEM_PROMPT},
            {"text": case_context(case, channel, self.reference_date)},
        ]
        options: dict[str, Any] = {
            "system": system,
            "inferenceConfig": {"maxTokens": self.max_tokens},
        }
        if self.tools.names:
            options["toolConfig"] = build_tool_config(self.tools.names)
        ctx = ToolContext(case=case, reference_date=self.reference_date)

        reply = AgentReply(text="")
        for _ in range(self.max_iterations):
            response = self.client.converse(messages, **options)
            output = response["output"]["message"]
            messages.append(output)
            if response.get("stopReason") != "tool_use":
                reply.text = "\n".join(
                    block["text"] for block in output["content"] if "text" in block
                ).strip()
                break
            results = []
            for block in output["content"]:
                if "toolUse" not in block:
                    continue
                use = block["toolUse"]
                envelope = self.tools.call(use["name"], ctx, use.get("input") or {})
                reply.tool_calls.append(ToolCall(name=use["name"], ok=envelope["ok"]))
                results.append(
                    {
                        "toolResult": {
                            "toolUseId": use["toolUseId"],
                            "content": [{"json": envelope}],
                            "status": "success" if envelope["ok"] else "error",
                        }
                    }
                )
            messages.append({"role": "user", "content": results})
        else:
            reply.text = LIMIT_REPLY
            reply.hit_iteration_limit = True

        case.messages.append(
            Message(role=MessageRole.AGENT, channel=channel, text=reply.text, created_at=now)
        )
        return reply
