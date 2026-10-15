import json
from math import hypot

import pytest

from src.app.ruta.despliegue import _project, _unproject, propose_campaign_area


def location(x, y, commune="Santiago"):
    longitude, latitude = _unproject(x, y)
    return {
        "latitude": latitude,
        "longitude": longitude,
        "weight": 1,
        "commune": commune,
        "synthetic": True,
        "address": "PRIVATE-ADDRESS",
    }


def test_selects_densest_cluster_and_exports_no_personal_details():
    points = [location(i * 20, 0) for i in range(7)]
    points += [location(10000 + i * 20, 0, "Maipú") for i in range(5)]
    area = propose_campaign_area(points, radius_m=500)
    info = area["properties"]
    assert info["people"] == 7 and info["total_mapped"] == 12
    assert info["coverage_percent"] == 58.3
    assert info["communes"] == {"Santiago": 7}
    assert "PRIVATE-ADDRESS" not in json.dumps(area)
    assert area["geometry"]["coordinates"][0][0] == area["geometry"]["coordinates"][0][-1]
    assert propose_campaign_area(list(reversed(points)), radius_m=500) == area


def test_search_can_place_center_between_people_instead_of_on_a_person():
    points = [location(-400, i) for i in range(3)] + [location(400, i) for i in range(3)]
    area = propose_campaign_area(points, radius_m=500)
    info = area["properties"]
    assert info["people"] == 6
    x, y = _project(info["center_latitude"], info["center_longitude"])
    assert abs(x) < 1 and abs(y - 1) < 1
    for point in points:
        px, py = _project(point["latitude"], point["longitude"])
        assert hypot(px - x, py - y) <= 500 + 1e-6


def test_radius_changes_coverage_and_capacity_changes_days_not_geometry():
    points = [location(i * 20, 0) for i in range(6)]
    points += [location(2000 + i * 20, 0, "Maipú") for i in range(5)]
    small = propose_campaign_area(points, radius_m=500, staff=1, daily_capacity=2)
    big = propose_campaign_area(points, radius_m=1500)
    assert small["properties"]["people"] == 6
    assert small["properties"]["estimated_days"] == 3
    assert big["properties"]["people"] == 11
    fast = propose_campaign_area(points, radius_m=500, staff=3, daily_capacity=8)
    assert fast["geometry"] == small["geometry"]
    assert fast["properties"]["estimated_days"] == 1


def test_no_proposal_with_less_than_five_nearby_people():
    assert propose_campaign_area([]) is None
    assert propose_campaign_area([location(i * 20, 0) for i in range(4)]) is None
    assert propose_campaign_area([location(i * 10000, 0) for i in range(5)], radius_m=500) is None


@pytest.mark.parametrize(
    "kwargs",
    [
        {"radius_m": 0},
        {"radius_m": True},
        {"radius_m": float("nan")},
        {"staff": 0},
        {"staff": True},
        {"daily_capacity": 1.5},
    ],
)
def test_invalid_policy_is_rejected(kwargs):
    with pytest.raises(ValueError):
        propose_campaign_area([], **kwargs)


def test_actual_or_invalid_locations_are_not_accepted():
    point = location(0, 0)
    for change in [{"synthetic": False}, {"weight": 2}, {"latitude": float("nan")}]:
        with pytest.raises(ValueError):
            propose_campaign_area([{**point, **change}])


def test_actual_demo_area_uses_same_map_population_and_tracks_case_changes(tmp_path):
    from src.app.ruta.campanas import metropolitan_locations, metropolitan_ranking
    from src.app.ruta.colador import Funnel
    from src.app.ruta.contacto import generate_contacts
    from src.app.ruta.datos import cargar_perfiles

    profiles = cargar_perfiles()
    engine = Funnel(tmp_path / "area.db")
    engine.initialize(profiles, generate_contacts(profiles, territory="metropolitana"))
    state = engine.advance(19)

    def compute(state):
        rows = metropolitan_ranking(state, profiles)
        points = metropolitan_locations(state, rows)
        return propose_campaign_area(points), points

    area, points = compute(state)
    info = area["properties"]
    assert info["total_mapped"] == len(points) == 84
    assert info["people"] == 10 and info["communes"] == {"San Bernardo": 10}
    x, y = _project(info["center_latitude"], info["center_longitude"])
    members = [
        p
        for p in state["people"]
        if p["contact"]["commune"] == "San Bernardo"
        and hypot(
            *[
                a - b
                for a, b in zip(
                    _project(p["contact"]["latitude"], p["contact"]["longitude"]),
                    (x, y),
                    strict=True,
                )
            ]
        )
        <= 1500 + 1e-6
    ]
    engine.respond(members[0]["run"], "declined")
    later, _ = compute(engine.snapshot())
    assert later["properties"]["total_mapped"] == 83
    assert later["properties"]["people"] <= info["people"]


def test_ui_area_overlay_and_radius_are_connected(tmp_path, monkeypatch):
    from pathlib import Path

    from streamlit.testing.v1 import AppTest

    root = Path(__file__).resolve().parents[1]
    monkeypatch.syspath_prepend(str(root / "src/app"))
    monkeypatch.setenv("FUNNEL_DEMO_DB", str(tmp_path / "area-ui.db"))
    app = AppTest.from_file(str(root / "src/app/demo_embudo.py"), default_timeout=30).run()
    app.radio[0].set_value("Sin respuestas")
    for label in ("Inicializar embudo", "Avanzar 19 días"):
        next(b for b in app.button if b.label == label).click().run()
        assert not app.exception

    def feature():
        payload = json.loads(app.get("deck_gl_json_chart")[0].proto.json)
        return next(
            layer["data"] for layer in payload["layers"] if layer["id"] == "rm-campaign-area"
        )

    assert feature()["properties"]["people"] == 10
    app.slider[0].set_value(3000).run()
    assert not app.exception
    assert feature()["properties"]["radius_m"] == 3000
    assert feature()["properties"]["people"] >= 10
    next(c for c in app.checkbox if c.label == "Mostrar área propuesta en el mapa").uncheck().run()
    payload = json.loads(app.get("deck_gl_json_chart")[0].proto.json)
    assert all(layer["id"] != "rm-campaign-area" for layer in payload["layers"])
    next(box for box in app.selectbox if box.label == "Población del mapa").select_index(1).run()
    assert not app.exception
    payload = json.loads(app.get("deck_gl_json_chart")[0].proto.json)
    assert all(layer["id"] != "rm-campaign-area" for layer in payload["layers"])
