"""Local CLI for the agent: `uv run agente --run <RUN>` (T04).

Demo only: the invitation and the authorization are simulated as accepted.
In the product they come from the API flow (T21), never from the chat.
"""

import argparse
import sys
from datetime import date, datetime

from src.agent.bedrock import BedrockClient
from src.agent.loop import Agent
from src.agent.tools import build_registry
from src.contracts import (
    Authorization,
    Case,
    Channel,
    Invitation,
    InvitationResponse,
)
from src.tools.profiles import normalize_run

DATASET_REFERENCE_DATE = date(2026, 10, 8)
FIRST_MESSAGE = "Hola, me estoy acercando a la jubilación. ¿Qué me corresponde y qué hago ahora?"


def demo_case(run: str, channel: Channel, now: datetime) -> Case:
    return Case(
        case_id=f"demo-{run}",
        run=run,
        created_at=now,
        invitation=Invitation(
            reason="Se acerca un hito de jubilación o PGU",
            channel=channel,
            sent_at=now,
            response=InvitationResponse.ACCEPTED,
            responded_at=now,
        ),
        authorization=Authorization(
            granted=True,
            sources=["Registro Civil", "RSH", "Residencia", "Previsión", "IPS"],
            purpose="Preparar tu ruta de jubilación y PGU (autorización simulada de demo)",
            channel=channel,
            decided_at=now,
        ),
    )


def print_case(case: Case) -> None:
    if case.pgu_result:
        print(f"\nResultado preliminar PGU: {case.pgu_result.status.value}")
    for milestone in case.milestones:
        print(f"Hito: {milestone.date} · {milestone.description}")
    for step in case.route:
        print(f"Paso {step.order}: {step.title}")
    for item in case.checklist:
        print(f"[ ] {item.label}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="agente", description=__doc__)
    parser.add_argument("--run", required=True, help="RUN del caso, con o sin puntos")
    parser.add_argument("--mensaje", help="Un solo mensaje; sin esto se abre un chat")
    parser.add_argument("--canal", default="web", choices=[c.value for c in Channel])
    parser.add_argument("--fecha", type=date.fromisoformat, default=DATASET_REFERENCE_DATE)
    args = parser.parse_args(argv)
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):  # Windows consoles default to cp1252
            stream.reconfigure(encoding="utf-8", errors="replace")

    now = datetime.now()
    channel = Channel(args.canal)
    case = demo_case(normalize_run(args.run), channel, now)
    registry = build_registry()
    agent = Agent(client=BedrockClient.from_env(), tools=registry, reference_date=args.fecha)
    print(f"Herramientas disponibles: {', '.join(registry.names)}")

    message = args.mensaje or FIRST_MESSAGE
    while message:
        reply = agent.run_turn(case, message, channel=channel)
        print(f"\nAgente: {reply.text}")
        if args.mensaje:
            break
        try:
            message = input("\nTú (Enter para salir): ").strip()
        except EOFError:
            break
    print_case(case)
    return 0


if __name__ == "__main__":
    sys.exit(main())
