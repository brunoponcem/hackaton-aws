import json

import pytest

from src.app.ruta.campanas import metropolitan_ranking
from src.app.ruta.contacto import generate_contacts
from src.app.ruta.datos import cargar_perfiles


def state_with(communes):
    return {
        "clock": {"now": "2026-10-27T09:00:00", "start": "2026-10-08T09:00:00"},
        "people": [
            {
                "run": f"PRIVATE-{i}",
                "name": "Nombre privado",
                "status": "active",
                "stage": 4,
                "contact": {
                    "synthetic": True,
                    "region": "Metropolitana de Santiago",
                    "province": "Santiago",
                    "commune": commune,
                },
            }
            for i, commune in enumerate(communes)
        ],
    }


def test_rm_generation_is_reproducible_without_changing_contact_channels():
    profiles = cargar_perfiles()
    national = generate_contacts(profiles)
    metro = generate_contacts(profiles, territory="metropolitana")
    assert metro == generate_contacts(
        dict(reversed(list(profiles.items()))), territory="metropolitana"
    )
    assert {row.region for row in metro.values()} == {"Metropolitana de Santiago"}
    assert len({row.commune for row in metro.values()}) == 8
    for run, row in metro.items():
        assert (row.email, row.phone, row.employer) == (
            national[run].email,
            national[run].phone,
            national[run].employer,
        )
    with pytest.raises(ValueError):
        generate_contacts(profiles, territory="unknown")


def test_commune_suppression_is_stricter_than_province_threshold():
    state = state_with(["Maipú"] * 5 + ["Pudahuel"] * 4)
    rows = metropolitan_ranking(state, {})
    assert [(r["commune"], r["people"]) for r in rows] == [("Maipú", 5)]
    payload = json.dumps(rows, ensure_ascii=False)
    assert all(secret not in payload for secret in ("PRIVATE", "Nombre privado", "Pudahuel"))
    state["people"][0]["status"] = "declined"
    assert metropolitan_ranking(state, {}) == []


@pytest.mark.parametrize(
    "change",
    [
        {"region": "Valparaíso"},
        {"province": "Cordillera"},
        {"synthetic": False},
        {"commune": "Desconocida"},
    ],
)
def test_no_outside_or_mismatched_territory_is_remapped_to_santiago(change):
    state = state_with(["Santiago"] * 8)
    for p in state["people"]:
        p["contact"].update(change)
    assert not metropolitan_ranking(state, {})


def test_metropolitan_counts_shrink_after_start_or_decline_and_exclude_remote():
    state = state_with(["Santiago"] * 8)
    state["people"][0]["status"] = "started"
    state["people"][1]["status"] = "declined"
    state["people"][2]["stage"] = 2
    assert metropolitan_ranking(state, {})[0]["people"] == 5
    assert metropolitan_ranking(state, {}, scope="active")[0]["people"] == 6
    assert not metropolitan_ranking({"clock": None}, {})
    with pytest.raises(ValueError):
        metropolitan_ranking(state, {}, scope="invalid")


def test_rm_scenario_conserves_people_and_has_nonuniform_hotspots(tmp_path):
    from src.app.ruta.colador import Funnel

    profiles = cargar_perfiles()
    engine = Funnel(tmp_path / "rm.db")
    engine.initialize(profiles, generate_contacts(profiles, territory="metropolitana"))
    state = engine.advance(19)
    rows = metropolitan_ranking(state, profiles)
    assert state["totals"]["in_person"] == 92
    assert len(rows) >= 4
    assert len({row["people"] for row in rows}) >= 3
    assert sum(row["people"] for row in rows) <= 92
    assert all(-34 < row["latitude"] < -33 and -71 < row["longitude"] < -70 for row in rows)
    assert rows == metropolitan_ranking(
        {**state, "people": list(reversed(state["people"]))}, profiles
    )


def test_map_labels_color_bins_and_heat_resolution_are_consistent(monkeypatch):
    from pathlib import Path

    monkeypatch.syspath_prepend(str(Path(__file__).resolve().parents[1] / "src/app"))
    from ui_campanas import campaign_map, concentration_color

    rows = metropolitan_ranking(state_with(["Maipú"] * 23 + ["Santiago"] * 6), {})
    payload = json.loads(campaign_map(rows).to_json())
    heat = next(layer for layer in payload["layers"] if layer["@@type"] == "HeatmapLayer")
    assert heat["weightsTextureSize"] == 2048
    labels = next(layer for layer in payload["layers"] if layer["@@type"] == "TextLayer")
    assert labels["characterSet"] == "auto"  # Literal, never the undefined accessor @@=auto.
    points = next(layer for layer in payload["layers"] if layer["@@type"] == "ScatterplotLayer")[
        "data"
    ]
    assert [p["people"] for p in points] == [23, 6]
    assert [p["color"] for p in points] == [concentration_color(23), concentration_color(6)]
    assert "23  Maipú" in [p["label"] for p in points]
    assert concentration_color(24) == concentration_color(20)
    assert concentration_color(25) != concentration_color(24)
    assert len(payload["layers"][0]["data"]["features"]) == 52
    assert "PRIVATE" not in json.dumps(payload)
