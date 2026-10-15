import copy
import json
import sqlite3
from pathlib import Path

import pytest

from src.app.ruta.colador import Funnel
from src.app.ruta.contacto import Contact, generate_contacts
from src.app.ruta.datos import cargar_perfiles

RUN = "100000001-5"


@pytest.fixture
def engine(tmp_path, monkeypatch):
    from src.app.ruta import config

    profile = copy.deepcopy(cargar_perfiles()[RUN])
    profile["registro_civil"]["fecha_nacimiento"] = "1956-10-08"
    profile["rsh"].update(info_pfp_disponible=True, pfp_percentil=50)
    profile["residencia"].update(
        resultado="cumple", anios_residencia_desde_20=30, anios_residencia_ultimos_5=5
    )
    profile["prevision"]["pafe_estimada"] = 0
    profile["pensiones_beneficios"] = []
    monkeypatch.setattr(config, "DB_PATH", tmp_path / "confirmed.db")
    funnel = Funnel()
    funnel.initialize(
        {RUN: profile},
        {
            RUN: Contact(
                RUN, "demo@example.com", "SIM-TEL", "Empresa ficticia", "RM", "Santiago", "Santiago"
            )
        },
    )
    return funnel


@pytest.mark.parametrize("response", ["answered", "contacted"])
def test_email_response_stops_all_later_channels_without_claiming_procedure_start(engine, response):
    first = engine.respond(RUN, response)
    assert first["people"][0]["status"] == "contacted"
    assert first["people"][0]["next_at"] is None
    assert first["totals"]["confirmed_contacts"] == 1
    assert first["totals"]["started"] == 0
    later = engine.advance(100)
    assert later["events"] == first["events"]
    assert all(row["attempts"] == 0 for row in later["funnel"][1:])
    assert engine.respond(RUN, response)["events"] == first["events"]
    with sqlite3.connect(engine.db_path) as con:
        assert con.execute("SELECT autorizacion FROM casos WHERE run=?", (RUN,)).fetchone()[0] == 0


def test_answering_first_call_stops_repeat_calls_and_work_contact(engine):
    engine.advance(7)
    engine.respond(RUN, "answered")
    state = engine.advance(100)
    assert state["funnel"][1]["attempts"] == 1
    assert state["funnel"][2]["attempts"] == 0
    assert state["totals"]["in_person"] == 0


def test_opening_without_reply_remains_active_and_then_escalates(engine):
    engine.respond(RUN, "opened")
    state = engine.advance(7)
    assert state["people"][0]["status"] == "active"
    assert state["funnel"][1]["attempts"] == 1


@pytest.mark.parametrize("next_response", ["started", "declined"])
def test_contacted_person_can_continue_procedure_or_decline_without_recontact(
    engine, next_response
):
    engine.respond(RUN, "contacted")
    engine.respond(RUN, next_response)
    state = Funnel(engine.db_path).advance(100)
    assert state["people"][0]["status"] == next_response
    assert state["funnel"][0]["attempts"] == 1
    assert state["funnel"][1]["attempts"] == 0


def test_case_progress_after_acceptance_is_synchronized_separately(engine):
    from src.app.ruta import casos

    casos.responder_invitacion(RUN, True, "Web")
    assert engine.snapshot()["people"][0]["status"] == "contacted"
    casos.completar_paso(RUN, "G1", "Web")
    assert engine.snapshot()["people"][0]["status"] == "started"


def test_old_answer_event_stops_future_contact_without_erasing_history(engine):
    engine.advance(7)
    with sqlite3.connect(engine.db_path) as con:
        con.execute(
            "INSERT INTO funnel_events(run,at,stage,kind,detail) VALUES(?,?,2,'answered','{}')",
            (RUN, "2026-10-15T09:00:00"),
        )
    state = engine.advance(100)
    assert state["people"][0]["status"] == "contacted"
    assert state["funnel"][1]["attempts"] == 1
    assert state["funnel"][2]["attempts"] == 0


def test_255_are_call_attempts_for_85_people_not_255_detected(tmp_path):
    profiles = cargar_perfiles()
    engine = Funnel(tmp_path / "no-response.db")
    engine.initialize(profiles, generate_contacts(profiles, territory="metropolitana"))
    state = engine.advance(19)
    phone = state["funnel"][1]
    assert len(profiles) == 500 and state["totals"]["detected"] == 92
    assert phone["attempts"] == 255 and phone["attempted"] == 85 and phone["skipped"] == 7
    assert state["totals"]["confirmed_contacts"] == 0
    assert state["totals"]["in_person"] == 92


def test_ui_confirmed_email_stops_contact_but_allows_start(tmp_path, monkeypatch):
    from streamlit.testing.v1 import AppTest

    root = Path(__file__).resolve().parents[1]
    monkeypatch.syspath_prepend(str(root / "src/app"))
    path = tmp_path / "ui.db"
    monkeypatch.setenv("FUNNEL_DEMO_DB", str(path))
    app = AppTest.from_file(str(root / "src/app/demo_embudo.py"), default_timeout=30).run()
    app.radio[0].set_value("Sin respuestas")

    def click(label):
        next(b for b in app.button if b.label == label).click().run()
        assert not app.exception

    click("Inicializar embudo")
    person = next(p for p in Funnel(path).snapshot()["people"] if p["stage"] == 1)
    next(box for box in app.selectbox if box.label == "Inspeccionar persona").select(
        person["run"]
    ).run()
    click("Abrió el correo")
    click("Confirmar contacto")
    assert next(m for m in app.metric if m.label == "Contacto confirmado").value == "1"
    assert next(m for m in app.metric if m.label == "Iniciaron trámite").value == "0"
    click("Avanzar 19 días")
    state = Funnel(path).snapshot()
    attempts = [e for e in state["events"] if e["run"] == person["run"] and e["kind"] == "attempt"]
    assert len(attempts) == 1 and attempts[0]["stage"] == 1
    click("Inició su trámite")
    assert next(m for m in app.metric if m.label == "Iniciaron trámite").value == "1"
    assert (
        next(m for m in app.metric if m.label == "Próximo paso válido dentro del plazo").value
        == "Sin medir"
    )
    assert json.loads(app.get("deck_gl_json_chart")[0].proto.json)["mapStyle"]
