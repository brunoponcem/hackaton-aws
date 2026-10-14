import json
from datetime import date, datetime
from pathlib import Path

import pytest
from pydantic import ValidationError

from src.contracts import (
    Authorization,
    Case,
    Channel,
    Invitation,
    InvitationResponse,
    Milestone,
    MilestoneKind,
    PguResult,
    PguStatus,
    Profile,
    RecordStatus,
)

PROFILES_PATH = Path("data/raw/dataset_A_participantes/perfiles.json")
NOW = datetime(2026, 10, 14, 12, 0)


@pytest.fixture(scope="module")
def raw_profiles():
    return json.loads(PROFILES_PATH.read_text(encoding="utf-8"))


def test_all_dataset_profiles_load(raw_profiles):
    profiles = [Profile.model_validate(raw) for raw in raw_profiles]
    assert len(profiles) == 500
    assert sum(p.rsh is None for p in profiles) == 3
    assert sum(p.residence is None for p in profiles) == 3
    assert sum(p.pension_fund is None for p in profiles) == 88


def test_profile_maps_dataset_keys(raw_profiles):
    raw = next(r for r in raw_profiles if r["pensiones_beneficios"])
    profile = Profile.model_validate(raw)
    assert profile.civil_registry.birth_date == date.fromisoformat(
        raw["registro_civil"]["fecha_nacimiento"]
    )
    assert profile.pensions_benefits[0].status in set(RecordStatus)


def test_profile_rejects_malformed_run(raw_profiles):
    raw = {**raw_profiles[0], "run": "100.000.001-5"}
    with pytest.raises(ValidationError):
        Profile.model_validate(raw)


def test_pgu_result_is_always_preliminary():
    result = PguResult(run="100000001-5", status=PguStatus.UPCOMING, reference_date=date.today())
    assert result.preliminary is True
    with pytest.raises(ValidationError):
        PguResult(
            run="100000001-5",
            status=PguStatus.ELIGIBLE,
            reference_date=date.today(),
            preliminary=False,
        )


def _case(**overrides):
    return Case(case_id="c-1", run="100000001-5", created_at=NOW, **overrides)


def _invitation(response):
    return Invitation(
        reason="Se acerca tu edad legal de jubilación",
        milestone=Milestone(
            kind=MilestoneKind.PGU_APPLICATION_OPENS,
            date=date(2027, 7, 1),
            description="Puedes solicitar la PGU desde esta fecha",
        ),
        channel=Channel.WEB,
        sent_at=NOW,
        response=response,
    )


def _authorization(granted):
    return Authorization(
        granted=granted,
        sources=["Registro Civil", "RSH"],
        purpose="Preparar tu ruta de jubilación",
        channel=Channel.WEB,
        decided_at=NOW,
    )


@pytest.mark.parametrize(
    ("response", "granted", "expected"),
    [
        (InvitationResponse.ACCEPTED, True, True),
        (InvitationResponse.ACCEPTED, False, False),
        (InvitationResponse.DECLINED, True, False),
        (InvitationResponse.PENDING, True, False),
    ],
)
def test_profile_access_requires_acceptance_and_consent(response, granted, expected):
    case = _case(invitation=_invitation(response), authorization=_authorization(granted))
    assert case.can_read_profile is expected


def test_no_authorization_means_no_profile_access():
    assert _case().can_read_profile is False


def test_case_round_trips_through_json():
    case = _case(
        invitation=_invitation(InvitationResponse.ACCEPTED),
        authorization=_authorization(True),
    )
    assert Case.model_validate_json(case.model_dump_json()) == case
