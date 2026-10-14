"""Deterministic route and checklist built from a PGU result (never from the LLM).

Texts are general guidance pending the verified catalog (T09/T14). Every step
cites the PGU ficha as an unverified source until T09 provides the official URL.
"""

from src.contracts import (
    Channel,
    ChecklistItem,
    Milestone,
    MilestoneKind,
    PguResult,
    PguStatus,
    Requirement,
    RouteStep,
    Source,
)

PGU_SOURCE = Source(title="Ficha PGU ChileAtiende (por verificar en T09)", verified=False)

_MISSING_STEPS = {
    Requirement.PFP: (
        "Ingresa o actualiza tu Registro Social de Hogares",
        "Sin RSH no se puede revisar el requisito de focalización (PFP) de la PGU.",
        "rsh",
        "Registro Social de Hogares vigente",
    ),
    Requirement.RESIDENCE: (
        "Acredita tu residencia en Chile",
        "No hay registro de residencia para revisar ese requisito.",
        "residencia",
        "Antecedentes de residencia disponibles",
    ),
}


def _opening(milestones: list[Milestone]) -> Milestone | None:
    return next((m for m in milestones if m.kind == MilestoneKind.PGU_APPLICATION_OPENS), None)


def build_route(
    result: PguResult, milestones: list[Milestone]
) -> tuple[list[RouteStep], list[ChecklistItem]]:
    steps: list[tuple[str, str, Channel | None]] = []
    checklist: list[tuple[str, str]] = []
    available_from = None

    if result.status == PguStatus.MISSING_RECORD:
        for reason in result.reasons:
            if reason.met is None and reason.requirement in _MISSING_STEPS:
                title, description, item_id, label = _MISSING_STEPS[reason.requirement]
                steps.append((title, description, Channel.BRANCH))
                checklist.append((item_id, label))
        steps.append(
            (
                "Vuelve a pedir tu orientación",
                "Con los antecedentes completos se repite la evaluación del mismo caso.",
                None,
            )
        )
    elif result.status == PguStatus.UPCOMING:
        opening = _opening(milestones)
        available_from = opening.date if opening else None
        steps.append(
            (
                "Prepara tus antecedentes antes de la apertura",
                "Revisa que tu RSH y tus datos estén al día para solicitar a tiempo.",
                None,
            )
        )
        steps.append(
            (
                "Solicita la PGU cuando se abra el plazo",
                "La apertura de la solicitud es un hito, no un vencimiento.",
                Channel.WEB,
            )
        )
        checklist += [("rsh", "Registro Social de Hogares vigente"), ("solicitud", "Solicitud PGU")]
    elif result.status == PguStatus.ELIGIBLE:
        steps.append(
            (
                "Solicita la PGU",
                "Tu orientación es preliminar: el IPS revisa los requisitos y resuelve.",
                Channel.WEB,
            )
        )
        checklist += [("cedula", "Cédula de identidad vigente"), ("solicitud", "Solicitud PGU")]
    elif result.status == PguStatus.NOT_ELIGIBLE:
        steps.append(
            (
                "Revisa el motivo con un ejecutivo",
                "Puedes confirmar el requisito no cumplido y consultar otras alternativas.",
                Channel.BRANCH,
            )
        )
    else:
        steps.append(
            (
                "Revisa tu PGU vigente",
                "Ya registras la PGU; consulta pagos o cambios en ChileAtiende.",
                Channel.WEB,
            )
        )

    route = [
        RouteStep(
            order=index,
            title=title,
            description=description,
            channel=channel,
            available_from=available_from if title.startswith("Solicita") else None,
            source=PGU_SOURCE,
        )
        for index, (title, description, channel) in enumerate(steps, start=1)
    ]
    items = [ChecklistItem(item_id=i, label=label, source=PGU_SOURCE) for i, label in checklist]
    return route, items
