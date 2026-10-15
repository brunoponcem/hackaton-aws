"""Aggregate synthetic funnel snapshots for campaign planning, without personal data."""

from collections import defaultdict
from datetime import date
from math import ceil

from . import reglas
from .contacto import METROPOLITAN_COMMUNES

# Representative city points, approximate WGS84; NOT provincial centroids or homes.
PROVINCE_POINTS = {
    ("Metropolitana de Santiago", "Santiago"): (-33.45, -70.67),
    ("Valparaíso", "Valparaíso"): (-33.05, -71.62),
    ("Biobío", "Concepción"): (-36.83, -73.05),
    ("La Araucanía", "Cautín"): (-38.74, -72.60),
    ("Los Lagos", "Llanquihue"): (-41.47, -72.94),
    ("Tarapacá", "Iquique"): (-20.22, -70.14),
}
MIN_GROUP_SIZE = 5


def _priority_score(people, profiles, state):
    now = date.fromisoformat(state["clock"]["now"][:10])
    reference = date.fromisoformat(state["clock"]["start"][:10])
    score = 0
    for person in people:
        score += 1
        profile = profiles.get(person["run"])
        if profile is None:
            continue
        diagnosis = reglas.diagnosticar(profile, reference)
        score += 2 * (diagnosis.pgu.resultado == reglas.ELEGIBLE)
        score += diagnosis.pgu.resultado == reglas.ANTECEDENTE_FALTANTE
        milestones = (
            diagnosis.hitos.fecha_edad_legal,
            diagnosis.hitos.fecha_apertura_pgu,
            diagnosis.hitos.fecha_acceso_pgu,
        )
        score += any(0 <= (milestone - now).days <= 90 for milestone in milestones)
    return score


def metropolitan_ranking(state: dict, profiles: dict, *, scope="in_person") -> list[dict]:
    """Publish commune-level RM aggregates, with suppression BEFORE any map layer."""
    if scope not in {"in_person", "active"}:
        raise ValueError("Población de campaña no reconocida.")
    if not state.get("clock"):
        return []
    locations = {row[1]: row for row in METROPOLITAN_COMMUNES}
    groups = defaultdict(list)
    for person in state["people"]:
        contact = person["contact"]
        commune = contact.get("commune")
        if (
            person["status"] == "active"
            and (scope == "active" or person["stage"] == 4)
            and contact.get("synthetic")
            and contact.get("region") == "Metropolitana de Santiago"
            and commune in locations
            and contact.get("province") == locations[commune][0]
        ):
            groups[commune].append(person)
    rows = []
    for commune, people in groups.items():
        if len(people) < MIN_GROUP_SIZE:
            continue
        province, _, latitude, longitude, _ = locations[commune]
        score = _priority_score(people, profiles, state)
        rows.append(
            {
                "region": "Metropolitana de Santiago",
                "province": province,
                "commune": commune,
                "latitude": latitude,
                "longitude": longitude,
                "people": len(people),
                "score": score,
                "synthetic": True,
                "channel": "Operativo presencial"
                if scope == "in_person"
                else "Seguimiento por etapa",
            }
        )
    rows.sort(key=lambda row: (-row["people"], -row["score"], row["commune"]))
    return [{"rank": i, **row} for i, row in enumerate(rows, 1)]


def campaign_ranking(state: dict, profiles: dict, *, scope="in_person") -> list[dict]:
    """Suppress small groups BEFORE returning anything to map, controls or export.

    Demo priority per person: 1 base + 2 possible unclaimed PGU + 1 missing
    evidence + 1 milestone in the next 90 days. These are NOT eligibility rules.
    """
    if scope not in {"in_person", "active"}:
        raise ValueError("Población de campaña no reconocida.")
    if not state.get("clock"):
        return []
    groups = defaultdict(list)
    for person in state["people"]:
        if person["status"] != "active" or (scope == "in_person" and person["stage"] != 4):
            continue
        contact = person["contact"]
        territory = contact["region"], contact["province"]
        if not contact.get("synthetic") or territory not in PROVINCE_POINTS:
            continue
        groups[territory].append(person)
    rows = []
    for (region, province), people in sorted(groups.items()):
        if len(people) < MIN_GROUP_SIZE:
            continue
        score = _priority_score(people, profiles, state)
        latitude, longitude = PROVINCE_POINTS[region, province]
        rows.append(
            {
                "region": region,
                "province": province,
                "people": len(people),
                "score": score,
                "latitude": latitude,
                "longitude": longitude,
                "channel": "Operativo presencial"
                if scope == "in_person"
                else "Seguimiento por etapa",
                "synthetic": True,
            }
        )
    rows.sort(key=lambda row: (-row["score"], -row["people"], row["region"], row["province"]))
    return [{"rank": i, **row} for i, row in enumerate(rows, 1)]


def deployment_proposal(row: dict, *, staff: int, daily_capacity: int) -> dict:
    """An aggregate workload estimate, not a booking, route or dispatched campaign."""
    if any(type(value) is not int or value < 1 for value in (staff, daily_capacity)):
        raise ValueError("Personal y capacidad deben ser enteros positivos.")
    if row["people"] < MIN_GROUP_SIZE or row["channel"] != "Operativo presencial":
        raise ValueError(
            "Solo se planifican grupos presenciales publicados de al menos 5 personas."
        )
    return {
        **({"commune": row["commune"]} if "commune" in row else {}),
        "province": row["province"],
        "region": row["region"],
        "people": row["people"],
        "score": row["score"],
        "staff": staff,
        "people_per_staff_day": daily_capacity,
        "team_daily_capacity": staff * daily_capacity,
        "estimated_days": ceil(row["people"] / (staff * daily_capacity)),
        "channel": row["channel"],
        "status": "Propuesta simulada, sin despacho",
        "synthetic": True,
    }
