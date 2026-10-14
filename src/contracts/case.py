"""Case shared across channels: invitation, authorization, route, checklist, messages."""

from datetime import date, datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field

from src.contracts.evaluation import Milestone, PguResult, Source
from src.contracts.profile import RUN_PATTERN


class CaseModel(BaseModel):
    model_config = ConfigDict(extra="forbid", validate_assignment=True)


class Channel(StrEnum):
    WEB = "web"
    BRANCH = "sucursal"
    PHONE = "telefono"
    WHATSAPP = "whatsapp"


class InvitationResponse(StrEnum):
    PENDING = "pendiente"
    ACCEPTED = "aceptada"
    DECLINED = "declinada"


class Invitation(CaseModel):
    """Why we contact the person; they can accept or decline."""

    reason: str
    milestone: Milestone | None = None
    channel: Channel
    sent_at: datetime
    response: InvitationResponse = InvitationResponse.PENDING
    responded_at: datetime | None = None


class Authorization(CaseModel):
    """Consent to read the extended profile, with explicit sources and purpose."""

    granted: bool
    sources: list[str] = Field(min_length=1)
    purpose: str
    channel: Channel
    decided_at: datetime


class ChecklistStatus(StrEnum):
    PENDING = "pendiente"
    DONE = "hecho"
    NOT_APPLICABLE = "no_aplica"


class ChecklistItem(CaseModel):
    item_id: str
    label: str
    status: ChecklistStatus = ChecklistStatus.PENDING
    source: Source | None = None
    updated_at: datetime | None = None
    updated_from: Channel | None = None


class RouteStep(CaseModel):
    order: int = Field(ge=1)
    title: str
    description: str
    channel: Channel | None = None
    documents: list[str] = Field(default_factory=list)
    available_from: date | None = None
    source: Source | None = None


class MessageRole(StrEnum):
    PERSON = "persona"
    AGENT = "agente"
    OFFICER = "ejecutivo"
    SYSTEM = "sistema"


class Message(CaseModel):
    role: MessageRole
    channel: Channel
    text: str
    created_at: datetime


class LifeEvent(StrEnum):
    RETIREMENT = "jubilacion"


class Case(CaseModel):
    case_id: str
    run: str = Field(pattern=RUN_PATTERN)
    event: LifeEvent = LifeEvent.RETIREMENT
    created_at: datetime
    invitation: Invitation | None = None
    authorization: Authorization | None = None
    pgu_result: PguResult | None = None
    milestones: list[Milestone] = Field(default_factory=list)
    route: list[RouteStep] = Field(default_factory=list)
    checklist: list[ChecklistItem] = Field(default_factory=list)
    messages: list[Message] = Field(default_factory=list)

    @property
    def can_read_profile(self) -> bool:
        """The extended profile may be read only after acceptance and consent."""
        accepted = (
            self.invitation is None or self.invitation.response == InvitationResponse.ACCEPTED
        )
        return accepted and self.authorization is not None and self.authorization.granted
