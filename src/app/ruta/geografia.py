"""Deterministic fictional addresses inside RM commune polygons, never RSH geocoding."""

import hashlib
import json
import math
from functools import lru_cache
from pathlib import Path

from .contacto import METROPOLITAN_COMMUNES, stable_random

COMMUNE_CODES = {
    "Maipú": 13119,
    "Puente Alto": 13201,
    "La Florida": 13110,
    "Santiago": 13101,
    "San Bernardo": 13401,
    "Pudahuel": 13124,
    "Quilicura": 13125,
    "Recoleta": 13127,
}


@lru_cache(maxsize=1)
def commune_geometries():
    path = Path(__file__).resolve().parents[1] / "assets/metropolitana-comunas.geojson"
    data = json.loads(path.read_text(encoding="utf-8"))
    return {int(f["properties"]["cod_comuna"]): f["geometry"] for f in data["features"]}


def _in_ring(longitude, latitude, ring):
    inside = False
    for (x1, y1), (x2, y2) in zip(ring, [*ring[1:], ring[0]], strict=True):
        if (y1 > latitude) != (y2 > latitude):
            cross = (x2 - x1) * (latitude - y1) / (y2 - y1) + x1
            if longitude < cross:
                inside = not inside
    return inside


def inside_commune(commune, latitude, longitude):
    if commune not in COMMUNE_CODES:
        return False
    if not all(
        type(value) in (float, int) and math.isfinite(value) for value in (latitude, longitude)
    ):
        return False
    geometry = commune_geometries()[COMMUNE_CODES[commune]]
    polygons = (
        [geometry["coordinates"]] if geometry["type"] == "Polygon" else geometry["coordinates"]
    )
    return any(
        _in_ring(longitude, latitude, polygon[0])
        and not any(_in_ring(longitude, latitude, hole) for hole in polygon[1:])
        for polygon in polygons
    )


@lru_cache(maxsize=10000)
def simulated_location(run, commune, seed):
    """Several neighborhood clusters plus dispersed cases, clipped to actual commune.

    Coordinates are exact for the simulation only. No street network lookup or
    matching to real homes is performed; urban reference anchors are illustrative.
    """
    if commune not in COMMUNE_CODES:
        return None
    _, _, center_lat, center_lon, _ = next(r for r in METROPOLITAN_COMMUNES if r[1] == commune)
    rng = stable_random(seed, run, "fictional-address-v1")
    # Independent local clusters spread across the urban reference area (about 2–6 km).
    offsets = ((0, 0), (0.018, 0.020), (-0.018, -0.024), (0.012, -0.031))
    offset_lat, offset_lon = rng.choices(offsets, weights=[4, 3, 2, 1])[0]
    spread = 0.006 if rng.random() < 0.7 else 0.018
    for _ in range(1000):
        latitude = round(rng.gauss(center_lat + offset_lat, spread), 6)
        longitude = round(rng.gauss(center_lon + offset_lon, spread * 1.25), 6)
        if inside_commune(commune, latitude, longitude):
            tag = hashlib.sha256(str(run).encode()).hexdigest()[:8].upper()
            return {
                "address": (
                    f"Pasaje Ficticio {tag} #{rng.randrange(100, 9999)}, {commune} (SIMULADA)"
                ),
                "latitude": latitude,
                "longitude": longitude,
                "location_source": "synthetic-address-v1",
            }
    raise ValueError(f"No se pudo generar una ubicación dentro de {commune}.")


def with_simulated_location(contact, run, seed):
    """Enrich legacy snapshots without changing their stored contacts or statuses."""
    if (
        not contact.get("synthetic")
        or contact.get("region") != "Metropolitana de Santiago"
        or contact.get("commune") not in COMMUNE_CODES
    ):
        return dict(contact)
    if contact.get("latitude") is not None or contact.get("longitude") is not None:
        return dict(
            contact
        )  # Supplied locations are validated by consumers, not silently replaced.
    return {**contact, **simulated_location(run, contact["commune"], seed)}
