"""Use the shared tool-use agent with the Streamlit route as trusted context."""

from datetime import UTC, datetime

from src.agent.bedrock import BedrockClient
from src.agent.loop import Agent
from src.agent.tools import ToolRegistry
from src.contracts import Authorization, Case, Channel, Message, MessageRole

from . import config


def answer(question: str, context: dict, history: list[dict], *, client=None) -> str:
    if not context.get("autorizado"):
        raise PermissionError("El chatbot requiere autorización antes de leer tu ruta.")
    now = datetime.now(UTC)
    case = Case(
        case_id=f"streamlit-{context['run']}",
        run=context["run"],
        created_at=now,
        authorization=Authorization(
            granted=True,
            sources=["Dataset A sintético"],
            purpose="Orientación y seguimiento del trámite autorizado en la app",
            channel=Channel.WEB,
            decided_at=now,
        ),
    )
    for message in history[-6:]:
        case.messages.append(
            Message(
                role=(MessageRole.AGENT if message["rol"] == "assistant" else MessageRole.PERSON),
                channel=Channel.WEB,
                text=message["texto"],
                created_at=now,
            )
        )
    registry = ToolRegistry()
    registry.register(
        "leer_caso",
        lambda trusted, args: {
            "case_id": trusted.case.case_id,
            "context": context,
            "source": "Ruta determinista del MVP sobre dataset A sintético",
            "fuente_url": config.FUENTE_PGU,
            "sources_verified": False,
        },
    )
    agent = Agent(
        client=client or BedrockClient.from_env(),
        tools=registry,
        reference_date=config.FECHA_REFERENCIA,
    )
    return agent.run_turn(case, question).text
