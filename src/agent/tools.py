"""Server-side handlers for the agent tools (T04).

Handlers receive the trusted context (case, reference date) from the
application; the model only supplies the arguments declared in prompts.py.
Every result uses one envelope: {"ok": true, "data": ...} or
{"ok": false, "error": {"type": ..., "message": ...}}.
"""

from collections.abc import Callable
from dataclasses import dataclass
from datetime import date
from typing import Any

from src.agent.route import build_route
from src.contracts import Case, Milestone, PguResult, Profile
from src.tools.profiles import ProfileRepository, consultar_perfil

PguRule = Callable[[Profile, date], PguResult]
MilestonesRule = Callable[[Profile, date], list[Milestone]]


class ToolError(Exception):
    def __init__(self, error_type: str, message: str) -> None:
        super().__init__(message)
        self.error_type = error_type


@dataclass
class ToolContext:
    case: Case
    reference_date: date


Handler = Callable[[ToolContext, dict[str, Any]], Any]


def _authorized_profile(ctx: ToolContext, repository: ProfileRepository | None) -> Profile:
    profile = consultar_perfil(ctx.case.run, case=ctx.case, repository=repository)
    if profile is None:
        raise ToolError("not_found", "No hay un perfil para el RUN del caso.")
    return profile


def _dump(value: Any) -> Any:
    if isinstance(value, list):
        return [_dump(item) for item in value]
    return value.model_dump(mode="json") if hasattr(value, "model_dump") else value


class ToolRegistry:
    def __init__(self) -> None:
        self._handlers: dict[str, Handler] = {}

    def register(self, name: str, handler: Handler) -> None:
        self._handlers[name] = handler

    @property
    def names(self) -> list[str]:
        return list(self._handlers)

    def call(self, name: str, ctx: ToolContext, args: dict[str, Any]) -> dict[str, Any]:
        handler = self._handlers.get(name)
        if handler is None:
            return _error("unknown_tool", f"La herramienta {name} no está disponible.")
        try:
            return {"ok": True, "data": _dump(handler(ctx, args or {}))}
        except ToolError as exc:
            return _error(exc.error_type, str(exc))
        except PermissionError as exc:
            return _error("permission_denied", str(exc))
        except ValueError as exc:
            return _error("invalid_input", str(exc))
        except Exception:  # noqa: BLE001 - never leak internals to the model
            return _error("internal", "Error interno de la herramienta; no hay resultado.")


def _error(error_type: str, message: str) -> dict[str, Any]:
    return {"ok": False, "error": {"type": error_type, "message": message}}


def _load_rules() -> tuple[PguRule | None, MilestonesRule | None]:
    """Pick up Johann's rules (T11/T12) once they exist in `src.rules`."""
    try:
        from src import rules  # type: ignore[attr-defined]
    except ImportError:
        return None, None
    return getattr(rules, "evaluar_pgu", None), getattr(rules, "calcular_hitos", None)


def build_registry(
    *,
    repository: ProfileRepository | None = None,
    pgu_rule: PguRule | None = None,
    milestones_rule: MilestonesRule | None = None,
    load_default_rules: bool = True,
) -> ToolRegistry:
    """Register only the tools whose implementation exists."""
    if load_default_rules:
        default_pgu, default_milestones = _load_rules()
        pgu_rule = pgu_rule or default_pgu
        milestones_rule = milestones_rule or default_milestones

    registry = ToolRegistry()

    def consultar(ctx: ToolContext, args: dict[str, Any]) -> dict[str, Any]:
        profile = consultar_perfil(args.get("run", ""), case=ctx.case, repository=repository)
        if profile is None:
            raise ToolError("not_found", "No hay un perfil para ese RUN.")
        data = profile.model_dump(mode="json")
        if data.get("pension_fund"):
            data["pension_fund"].pop("contributions", None)
        return {"profile": data, "source": "Dataset A sintético (referencia 2026-10-08)"}

    def leer_caso(ctx: ToolContext, args: dict[str, Any]) -> dict[str, Any]:
        case = ctx.case
        return {
            "case_id": case.case_id,
            "event": case.event,
            "invitation": _dump(case.invitation),
            "authorized": case.can_read_profile,
            "pgu_result": _dump(case.pgu_result),
            "milestones": _dump(case.milestones),
            "route": _dump(case.route),
            "checklist": _dump(case.checklist),
            "recent_messages": _dump(case.messages[-10:]),
        }

    registry.register("consultar_perfil", consultar)
    registry.register("leer_caso", leer_caso)

    if pgu_rule is not None:

        def evaluar(ctx: ToolContext, args: dict[str, Any]) -> PguResult:
            result = pgu_rule(_authorized_profile(ctx, repository), ctx.reference_date)
            ctx.case.pgu_result = result
            ctx.case.route, ctx.case.checklist = build_route(result, ctx.case.milestones)
            return result

        registry.register("evaluar_pgu", evaluar)

    if milestones_rule is not None:

        def hitos(ctx: ToolContext, args: dict[str, Any]) -> list[Milestone]:
            milestones = milestones_rule(_authorized_profile(ctx, repository), ctx.reference_date)
            ctx.case.milestones = milestones
            if ctx.case.pgu_result is not None:
                ctx.case.route, ctx.case.checklist = build_route(ctx.case.pgu_result, milestones)
            return milestones

        registry.register("calcular_hitos", hitos)

    return registry
