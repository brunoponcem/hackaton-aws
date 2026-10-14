"""Output of the deterministic rules (PGU evaluation and milestones).

These results are preliminary guidance: the competent institution (IPS/AFP)
validates requirements and decides. `preliminary` is always True on purpose.
"""

import datetime as dt
from datetime import date
from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class ContractModel(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class Source(ContractModel):
    """Where a rule, amount or date comes from. Unverified values must say so."""

    title: str
    url: HttpUrl | None = None
    consulted_on: date | None = None
    verified: bool = False


class PguStatus(StrEnum):
    ELIGIBLE = "elegible"
    NOT_ELIGIBLE = "no_elegible"
    MISSING_RECORD = "antecedente_faltante"
    UPCOMING = "proximo"
    ALREADY_RECEIVES = "ya_recibe"


class Requirement(StrEnum):
    AGE = "edad"
    ALIVE = "vivo"
    PFP = "pfp"
    RESIDENCE = "residencia"
    BASE_PENSION = "pension_base"
    NO_ACTIVE_PGU = "sin_pgu_vigente"


class Reason(ContractModel):
    requirement: Requirement
    met: bool | None = Field(description="None when it cannot be evaluated (missing record).")
    message: str
    source: Source | None = None


class PguResult(ContractModel):
    run: str
    status: PguStatus
    reference_date: date
    reasons: list[Reason] = Field(default_factory=list)
    preliminary: Literal[True] = True


class MilestoneKind(StrEnum):
    LEGAL_RETIREMENT_AGE = "edad_legal_vejez"
    PGU_APPLICATION_OPENS = "apertura_solicitud_pgu"
    PGU_ACCESS = "acceso_pgu"
    INVITATION = "invitacion"


class Milestone(ContractModel):
    """A dated event in the person's path. Openings are not deadlines."""

    kind: MilestoneKind
    date: dt.date
    description: str
    is_deadline: bool = False
    source: Source | None = None
