import copy
import json
from collections import Counter
from dataclasses import asdict
from pathlib import Path

import pytest

from src.app.ruta.campanas import metropolitan_locations, metropolitan_ranking
from src.app.ruta.colador import Funnel
from src.app.ruta.contacto import generate_contacts, load_contacts, save_contacts
from src.app.ruta.datos import cargar_perfiles
from src.app.ruta.geografia import (
    _in_ring,
    inside_commune,
    simulated_location,
    with_simulated_location,
)


@pytest.fixture
def scenario(tmp_path):
    profiles = cargar_perfiles()
    engine = Funnel(tmp_path / "addresses.db")
    engine.initialize(profiles, generate_contacts(profiles, territory="metropolitana"))
    state = engine.advance(19)
    return engine, profiles, state


def test_all_500_locations_are_inside_their_commune_and_unique():
    profiles = cargar_perfiles()
    contacts = generate_contacts(profiles, territory="metropolitana")
    assert len({row.address for row in contacts.values()}) == 500
    assert len({(row.latitude, row.longitude) for row in contacts.values()}) == 500
    for row in contacts.values():
        assert inside_commune(row.commune, row.latitude, row.longitude)
        assert "SIMULADA" in row.address
    assert contacts == generate_contacts(
        dict(reversed(list(profiles.items()))), territory="metropolitana"
    )


def test_exact_contact_round_trip_and_old_csv_compatibility(tmp_path):
    contacts = generate_contacts(cargar_perfiles(), territory="metropolitana")
    path = tmp_path / "rm.csv"
    save_contacts(path, contacts)
    assert load_contacts(path) == contacts
    old = load_contacts(Path("data/synthetic/contacto.csv"))
    assert len(old) == 500 and all(row.latitude is None for row in old.values())


def test_heat_weight_conserves_counts_and_distribution_is_not_centroids(scenario):
    _, profiles, state = scenario
    rows = metropolitan_ranking(state, profiles)
    points = metropolitan_locations(state, rows)
    assert len(points) == sum(row["people"] for row in rows) == 84
    assert Counter(p["commune"] for p in points) == {r["commune"]: r["people"] for r in rows}
    for row in rows:
        local = [p for p in points if p["commune"] == row["commune"]]
        assert len({(p["latitude"], p["longitude"]) for p in local}) == row["people"]
        assert max(p["latitude"] for p in local) - min(p["latitude"] for p in local) > 0.008
    assert "run" not in points[0] and "name" not in points[0]


def test_old_snapshot_enrichment_preserves_case_and_is_stable(scenario):
    _, profiles, state = scenario
    legacy = copy.deepcopy(state)
    for p in legacy["people"]:
        for field in ("address", "latitude", "longitude", "location_source"):
            p["contact"].pop(field, None)
    original = copy.deepcopy(legacy)
    rows = metropolitan_ranking(legacy, profiles)
    actual = metropolitan_locations(legacy, rows)
    assert actual == metropolitan_locations(state, rows)
    assert legacy == original
    assert actual == metropolitan_locations(
        {**legacy, "people": list(reversed(legacy["people"]))}, rows
    )


def test_reopened_database_keeps_coordinates_and_removes_started_or_declined(scenario):
    engine, profiles, state = scenario
    rows = metropolitan_ranking(state, profiles)
    before = metropolitan_locations(state, rows)
    reopened = Funnel(engine.db_path)
    assert reopened.snapshot() == state
    people = [p for p in state["people"] if p["contact"]["commune"] == "Maipú"]
    engine.respond(people[0]["run"], "started")
    engine.respond(people[1]["run"], "declined")
    state = reopened.snapshot()
    after = metropolitan_locations(state, metropolitan_ranking(state, profiles))
    assert len(before) - len(after) == 2
    assert all(p in before for p in after)


@pytest.mark.parametrize(
    "coordinates",
    [(None, 0), (float("nan"), 0), (float("inf"), 0), (True, 0), (-40, -70), (-33.5, -71.9)],
)
def test_invalid_or_outside_coordinates_are_rejected(coordinates):
    assert not inside_commune("Maipú", *coordinates)


def test_holes_and_multipolygon_membership_and_unknown_territory(monkeypatch):
    ring = [(0, 0), (2, 0), (2, 2), (0, 2), (0, 0)]
    assert _in_ring(1, 1, ring) and not _in_ring(3, 1, ring)
    assert simulated_location("demo", "Desconocida", 1) is None
    assert not inside_commune("Desconocida", -33.5, -70.7)
    contact = asdict(next(iter(generate_contacts(cargar_perfiles()).values())))
    contact.update(synthetic=False, region="Metropolitana de Santiago", commune="Santiago")
    assert with_simulated_location(contact, "demo", 1) == contact
    from src.app.ruta import geografia

    hole = [(0.5, 0.5), (1.5, 0.5), (1.5, 1.5), (0.5, 1.5), (0.5, 0.5)]
    island = [(10, 10), (11, 10), (11, 11), (10, 11), (10, 10)]
    geometry = {"type": "MultiPolygon", "coordinates": [[ring, hole], [island]]}
    monkeypatch.setattr(geografia, "commune_geometries", lambda: {13119: geometry})
    assert inside_commune("Maipú", 0.25, 0.25)
    assert not inside_commune("Maipú", 1, 1)
    assert inside_commune("Maipú", 10.5, 10.5)
    assert not inside_commune("Maipú", 3, 3)


def test_corrupt_coordinate_is_omitted_instead_of_returning_to_center(scenario):
    _, profiles, state = scenario
    rows = metropolitan_ranking(state, profiles)
    before = metropolitan_locations(state, rows)
    target = next(p for p in state["people"] if p["contact"]["commune"] == "Maipú")
    target["contact"]["latitude"] = -40
    assert len(metropolitan_locations(state, rows)) == len(before) - 1


def test_map_uses_person_locations_and_optional_markers_without_commune_bubbles(
    scenario, monkeypatch
):
    monkeypatch.syspath_prepend(str(Path(__file__).resolve().parents[1] / "src/app"))
    from ui_campanas import campaign_map

    _, profiles, state = scenario
    rows = metropolitan_ranking(state, profiles)
    locations = metropolitan_locations(state, rows)
    payload = json.loads(campaign_map(rows, locations).to_json())
    heat = next(layer for layer in payload["layers"] if layer["id"] == "rm-heat")
    assert len(heat["data"]) == 84
    assert all(p["weight"] == 1 for p in heat["data"])
    assert all(layer["@@type"] != "ScatterplotLayer" for layer in payload["layers"])
    alternate = json.loads(
        campaign_map(rows, locations, show_points=True, show_heat=False).to_json()
    )
    assert all(layer["@@type"] != "HeatmapLayer" for layer in alternate["layers"])
    markers = next(layer for layer in alternate["layers"] if layer["id"] == "rm-simulated-homes")
    assert len(markers["data"]) == 84
    assert all("SIMULADA" in point["tooltip_detail"] for point in markers["data"])
