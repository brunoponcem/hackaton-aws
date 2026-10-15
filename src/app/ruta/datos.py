"""Carga de perfiles del dataset A (simula la interoperabilidad entre organismos)."""
import json
from functools import lru_cache

from . import config


@lru_cache(maxsize=1)
def cargar_perfiles() -> dict[str, dict]:
    """Devuelve {run: perfil}. Cada perfil trae bloques por organismo (null/[] si no aparece)."""
    with open(config.PERFILES_PATH, encoding="utf-8") as fh:
        perfiles = json.load(fh)
    return {p["run"]: p for p in perfiles}


def consultar_perfil(run: str) -> dict | None:
    return cargar_perfiles().get(run)


def nombre_completo(perfil: dict) -> str:
    rc = perfil["registro_civil"]
    return f'{rc["nombres"]} {rc["apellido_paterno"]} {rc["apellido_materno"]}'
