"""Verificación del motor sobre los 500 perfiles del dataset A.

Ejecutar:  .venv\\Scripts\\python verificar.py
Falla (exit 1) si alguna regla no cuadra con los conteos conocidos del dataset.
"""
import sys
import tempfile
from collections import Counter
from datetime import date
from pathlib import Path

from ruta import asistente, casos, config
from ruta import reglas as R
from ruta.datos import cargar_perfiles
from ruta.fechas import cumple, edad
from ruta.rutas import estado_pasos, generar_ruta, proximo_paso

# This verification must stay offline even when BEDROCK_MODEL_ID is exported.
config.BEDROCK_MODEL_ID = ""

sys.stdout.reconfigure(encoding="utf-8")
errores: list[str] = []


def check(cond: bool, msg: str) -> None:
    print(("OK   " if cond else "FAIL ") + msg)
    if not cond:
        errores.append(msg)


# --- Fechas (bordes) -------------------------------------------------------
check(cumple(date(1962, 1, 8), 64, 9) == date(2026, 10, 8), "64 años 9 meses exactos")
check(cumple(date(1960, 2, 29), 65) == date(2025, 2, 28), "29-feb + 65 años -> 28-feb")
check(edad(date(1961, 10, 8), date(2026, 10, 8)) == 65, "cumpleaños el mismo día cuenta")
check(edad(date(1961, 10, 9), date(2026, 10, 8)) == 64, "día antes del cumpleaños")

# --- Fórmula de monto ------------------------------------------------------
check(R.monto_pgu(0, 70) == (231_732, 231_732), "PGU completa con pensión base 0")
check(R.monto_pgu(1_252_602, 70)[1] == 0, "PGU 0 en pensión superior")
check(R.monto_pgu(0, 80)[0] == 250_275, "tramo 75+")
mid = (789_139 + 1_252_602) // 2
check(abs(R.monto_pgu(mid, 70)[1] - 231_732 / 2) < 2, "PGU parcial lineal al punto medio")

# --- Lote completo ---------------------------------------------------------
perfiles = cargar_perfiles()
diags = {run: R.diagnosticar(p) for run, p in perfiles.items()}
check(len(diags) == 500, "500 perfiles evaluados")

res = Counter(d.pgu.resultado for d in diags.values())
seg = Counter(d.segmento for d in diags.values())
print("\nResultados PGU:", dict(res))
print("Segmentos:", dict(seg), "\n")

check(res[R.EXCLUIDO] == 20, "20 fallecidos excluidos")
check(all(not d.invitar for d in diags.values() if not d.vivo), "ningún fallecido se invita")
check(res[R.YA_RECIBE] == 0, "ninguna PGU vigente en el dataset")
# Casos con PGU suspendida: cada uno debe tener un antecedente faltante identificado
for run in ("100000051-1", "100000232-8"):
    d = diags[run]
    check(d.pgu.resultado == R.ANTECEDENTE_FALTANTE and d.pgu.pgu_registro["estado"] == "suspendido",
          f"{run}: PGU suspendida -> antecedente_faltante ({d.pgu.motivo})")
check(diags["100000051-1"].pgu.requisitos[1].estado == R.FALTA, "100000051-1: falta RSH")
check(diags["100000232-8"].pgu.requisitos[2].estado == R.FALTA, "100000232-8: falta residencia")

# Coherencia de reglas contra los datos crudos
for run, d in diags.items():
    p = perfiles[run]
    if d.pgu.resultado == R.ELEGIBLE:
        if not (d.hitos.edad >= 65 or config.FECHA_REFERENCIA >= d.hitos.fecha_apertura_pgu):
            errores.append(f"{run}: elegible sin edad")
        if p["rsh"]["pfp_percentil"] > 90 or p["residencia"]["resultado"] != "cumple":
            errores.append(f"{run}: elegible con PFP/residencia fuera de regla")
check(not [e for e in errores if "elegible" in e], "todo 'elegible' cumple edad, PFP y residencia en los datos")

# Las rutas se generan para todos los vivos y el próximo paso existe cuando hay ruta
sin_ruta_invitado = [r for r, d in diags.items() if d.invitar and not generar_ruta(d)]
check(not sin_ruta_invitado, f"toda persona invitada tiene ruta ({len(sin_ruta_invitado)} sin ruta)")
for run, d in diags.items():
    ruta = generar_ruta(d)
    ids = {p.id for p in ruta}
    for p in ruta:
        if not set(p.depende_de) <= ids:
            errores.append(f"{run}: paso {p.id} depende de un paso inexistente {p.depende_de}")
check(not [e for e in errores if "inexistente" in e], "dependencias de pasos válidas en las 500 rutas")

# Ruta del caso sin RSH: la solicitud PGU queda bloqueada hasta confirmar el RSH
d = diags["100000051-1"]
ruta = generar_ruta(d)
est = estado_pasos(ruta, set())
check(est["G1"] == "bloqueado" and est["A1"] == "disponible", "sin RSH: A1 disponible y G1 bloqueado")
est = estado_pasos(ruta, {"A1", "A2", "G0"})
check(est["G1"] == "disponible", "con RSH confirmado: se desbloquea la solicitud PGU")

# Asistente sin autorización no expone datos sensibles
ctx = asistente.construir_contexto(d, ruta, est, proximo_paso(ruta, est), autorizado=False)
check("pgu" not in ctx and "ruta" not in ctx, "contexto sin autorización no incluye RSH/previsión/pensiones")
ctx_ok = asistente.construir_contexto(d, ruta, est, proximo_paso(ruta, est), autorizado=True)
for q in ("¿Qué es la PGU?", "¿Cuánto recibiría?", "¿Qué documentos necesito?", "¿Cumplo los requisitos?"):
    r, motor = asistente.responder(q, ctx_ok, [])
    check(bool(r) and motor in ("plantillas", "bedrock"), f"asistente responde: {q}")

# Saludo y todas las preguntas rápidas, con y sin autorización, para las 500 personas
PREGUNTAS = ["¿Qué es la PGU?", "¿Cuánto recibiría?", "¿Qué documentos necesito?",
             "¿Cuándo puedo hacerlo?", "¿Dónde lo hago?", "¿Cumplo los requisitos?", "hola"]
fallos = []
for run, d in diags.items():
    ruta = generar_ruta(d)
    est = estado_pasos(ruta, set())
    for aut in (False, True):
        c = asistente.construir_contexto(d, ruta, est, proximo_paso(ruta, est), autorizado=aut)
        try:
            asistente.explicar_resumen(c)
            for q in PREGUNTAS:
                asistente.responder(q, c, [])
        except Exception as e:
            fallos.append(f"{run} aut={aut}: {type(e).__name__}: {e}")
check(not fallos, f"asistente sin errores en 500 perfiles x 2 estados x {len(PREGUNTAS) + 1} mensajes "
                  f"({len(fallos)} fallos{': ' + fallos[0] if fallos else ''})")

# --- Seguimiento SQLite (en BD temporal) -----------------------------------
config.DB_PATH = Path(tempfile.gettempdir()) / "casos_verificacion.db"
casos.reiniciar()
casos.invitar(["100000051-1"], "WhatsApp")
casos.responder_invitacion("100000051-1", True, "WhatsApp")
casos.autorizar("100000051-1", True, "Web ChileAtiende")
casos.completar_paso("100000051-1", "A1", "Sucursal ChileAtiende", "RSH")
c = casos.obtener_caso("100000051-1")
check(c["invitacion"] == "aceptado" and c["autorizacion"] == 1 and c["completados"] == {"A1"},
      "caso conserva invitación, autorización y pasos")
check(len({e["canal"] for e in c["eventos"]}) == 3, "historial con contexto entre 3 canales")
config.DB_PATH.unlink(missing_ok=True)

print(f"\n{'TODO OK' if not errores else f'{len(errores)} ERRORES'}")
for e in errores[:20]:
    print("  -", e)
sys.exit(1 if errores else 0)
