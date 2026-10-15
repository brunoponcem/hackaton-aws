"""Reproducible, non-contactable demo contacts; never changes the raw dataset."""

import csv
import hashlib
import random
from dataclasses import asdict, dataclass
from pathlib import Path

# Small illustrative selection, not a population distribution or geocoder.
# Reference: SUBDERE, Códigos Únicos Territoriales.
TERRITORIES = (
    ("Metropolitana de Santiago", "Santiago", "Santiago"),
    ("Valparaíso", "Valparaíso", "Valparaíso"),
    ("Biobío", "Concepción", "Concepción"),
    ("La Araucanía", "Cautín", "Temuco"),
    ("Los Lagos", "Llanquihue", "Puerto Montt"),
    ("Tarapacá", "Iquique", "Iquique"),
)


def stable_random(seed: int, *parts: object) -> random.Random:
    key = "|".join(map(str, (seed, *parts)))
    return random.Random(int.from_bytes(hashlib.sha256(key.encode()).digest()[:8], "big"))


@dataclass(frozen=True)
class Contact:
    run: str
    email: str
    phone: str
    employer: str
    region: str
    province: str
    commune: str
    synthetic: bool = True


def generate_contacts(profiles: dict[str, dict], seed: int = 20261008) -> dict[str, Contact]:
    contacts = {}
    for run, profile in sorted(profiles.items()):
        rng = stable_random(seed, run, "contact")
        territory = rng.choice(TERRITORIES)
        works = bool((profile.get("situacion_laboral") or {}).get("trabaja_actualmente"))
        contacts[run] = Contact(
            run=run,
            email=f"persona.{run}@example.com" if rng.random() >= 0.15 else "",
            phone=f"SIM-TEL-{run}" if rng.random() >= 0.1 else "",
            employer=f"Empleador ficticio {rng.randrange(1, 20)}" if works else "",
            region=territory[0],
            province=territory[1],
            commune=territory[2],
        )
    return contacts


def save_contacts(path: Path, contacts: dict[str, Contact]) -> None:
    """Exclusive creation: never overwrite a contact file supplied by a person."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(Contact.__dataclass_fields__))
        writer.writeheader()
        writer.writerows(asdict(contact) for _, contact in sorted(contacts.items()))


def load_contacts(path: Path) -> dict[str, Contact]:
    contacts = {}
    with path.open(encoding="utf-8", newline="") as stream:
        for row in csv.DictReader(stream):
            row["synthetic"] = str(row["synthetic"]).lower() == "true"
            contact = Contact(**row)
            if contact.run in contacts:
                raise ValueError("RUN duplicado en contactos.")
            contacts[contact.run] = contact
    return contacts
