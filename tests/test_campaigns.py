import copy
import json

import pytest

from src.app.ruta.campanas import campaign_ranking, deployment_proposal


def person(index, province="Santiago", region="Metropolitana de Santiago", **changes):
    return {
        "run": f"SIM-{index}",
        "name": "Nombre privado",
        "status": "active",
        "stage": 4,
        "contact": {"region": region, "province": province, "synthetic": True},
        **changes,
    }


def snapshot(people):
    return {
        "clock": {"now": "2026-10-27T09:00:00", "start": "2026-10-08T09:00:00"},
        "people": people,
    }


def test_suppresses_small_groups_and_never_exports_identifiers():
    people = [person(i) for i in range(5)] + [
        person(i + 10, "Cautín", "La Araucanía") for i in range(4)
    ]
    state = snapshot(people)
    original = copy.deepcopy(state)
    rows = campaign_ranking(state, {})
    assert len(rows) == 1 and rows[0]["people"] == 5
    encoded = json.dumps(rows, ensure_ascii=False)
    assert all(secret not in encoded for secret in ("SIM-", "Nombre privado", "Cautín", "run"))
    assert state == original


def test_terminal_and_remote_cases_are_excluded_and_scope_is_explicit():
    people = [person(i) for i in range(4)] + [person(5, stage=2)]
    people += [person(6, status="started"), person(7, status="declined")]
    assert not campaign_ranking(snapshot(people), {})
    assert campaign_ranking(snapshot(people), {}, scope="active")[0]["people"] == 5
    with pytest.raises(ValueError):
        campaign_ranking(snapshot(people), {}, scope="bad")


def test_unsupported_and_non_synthetic_territories_are_not_mislocated():
    people = [person(i, "Desconocida", "Región desconocida") for i in range(6)]
    people += [
        person(
            i + 10,
            contact={
                "region": "Metropolitana de Santiago",
                "province": "Santiago",
                "synthetic": False,
            },
        )
        for i in range(6)
    ]
    assert not campaign_ranking(snapshot(people), {})
    assert not campaign_ranking({"clock": None}, {})


def test_priority_uses_existing_rules_and_clock_and_ranking_is_stable(monkeypatch):
    from datetime import date
    from types import SimpleNamespace

    from src.app.ruta import reglas

    def diagnosis(profile, reference):
        assert reference == date(2026, 10, 8)
        return SimpleNamespace(
            pgu=SimpleNamespace(resultado=profile["pgu"]),
            hitos=SimpleNamespace(
                fecha_edad_legal=date(2026, 11, 1),
                fecha_apertura_pgu=date(2020, 1, 1),
                fecha_acceso_pgu=date(2020, 1, 1),
            ),
        )

    monkeypatch.setattr(reglas, "diagnosticar", diagnosis)
    people = [person(i) for i in range(5)] + [
        person(i + 10, "Cautín", "La Araucanía") for i in range(5)
    ]
    profiles = {
        p["run"]: {"pgu": reglas.ELEGIBLE if i < 5 else reglas.ANTECEDENTE_FALTANTE}
        for i, p in enumerate(people)
    }
    rows = campaign_ranking(snapshot(people), profiles)
    assert [(r["province"], r["score"]) for r in rows] == [("Santiago", 20), ("Cautín", 15)]
    assert rows == campaign_ranking(snapshot(list(reversed(people))), profiles)


def test_workload_proposal_has_no_dispatch_and_rounds_up():
    row = campaign_ranking(snapshot([person(i) for i in range(17)]), {})[0]
    result = deployment_proposal(row, staff=2, daily_capacity=8)
    assert result["estimated_days"] == 2 and result["team_daily_capacity"] == 16
    assert result["synthetic"] and "sin despacho" in result["status"]
    for staff, capacity in [(0, 8), (True, 8), (2, -1), (2, 1.5)]:
        with pytest.raises(ValueError):
            deployment_proposal(row, staff=staff, daily_capacity=capacity)
    row["channel"] = "Seguimiento por etapa"
    with pytest.raises(ValueError):
        deployment_proposal(row, staff=2, daily_capacity=8)


def test_visual_campaign_map_tracks_clock_and_filters(tmp_path, monkeypatch):
    from pathlib import Path

    from streamlit.testing.v1 import AppTest

    root = Path(__file__).resolve().parents[1]
    monkeypatch.syspath_prepend(str(root / "src/app"))
    monkeypatch.setenv("FUNNEL_DEMO_DB", str(tmp_path / "map.db"))
    app = AppTest.from_file(str(root / "src/app/demo_embudo.py"), default_timeout=30).run()

    def click(label):
        next(button for button in app.button if button.label == label).click().run()
        assert not app.exception

    app.radio[0].set_value("Sin respuestas")
    click("Inicializar embudo")
    click("Avanzar 19 días")
    assert len(app.get("deck_gl_json_chart")) == 1
    map_payload = json.loads(app.get("deck_gl_json_chart")[0].proto.json)
    assert map_payload["mapStyle"].startswith("https://basemaps.cartocdn.com/")
    assert map_payload["initialViewState"]["zoom"] > 10
    assert len(map_payload["layers"][0]["data"]["features"]) == 52
    assert "SIM-" not in json.dumps(map_payload)
    assert any("Propuesta:" in item.value for item in app.success)
    from src.app.ruta.colador import Funnel

    state = Funnel(tmp_path / "map.db").snapshot()
    from src.app.ruta.campanas import metropolitan_ranking
    from src.app.ruta.datos import cargar_perfiles

    rows = metropolitan_ranking(state, cargar_perfiles())
    assert len(rows) >= 4 and sum(row["people"] for row in rows) <= 92
    assert all(row["region"] == "Metropolitana de Santiago" for row in rows)
    next(box for box in app.selectbox if box.label == "Encuadre").select("Región completa").run()
    assert not app.exception
    assert json.loads(app.get("deck_gl_json_chart")[0].proto.json)["initialViewState"]["zoom"] < 9
    app.toggle[0].set_value(False).run()
    payload = json.loads(app.get("deck_gl_json_chart")[0].proto.json)
    assert all(layer["@@type"] != "HeatmapLayer" for layer in payload["layers"])
    next(box for box in app.selectbox if box.label == "Población del mapa").select_index(1).run()
    assert not app.exception
    assert not any(box.label == "Comuna para el despliegue" for box in app.selectbox)
