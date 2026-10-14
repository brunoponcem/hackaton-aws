---
tipo: bitacora-integrante
integrante: Clemente
---
# Bitácora de Clemente

Una entrada por avance o commit relevante, la más reciente arriba. Así se puede seguir el historial de cada tarea sin leer todo `git log`.

Formato: `### AAAA-MM-DD HH:MM · T<nn> · <commit corto>` y debajo qué se hizo, qué falta y si algo bloquea a otro integrante.

### 2026-10-14 · T02 · en curso (`clemente/T02-contratos`)
- Contratos compartidos en `src/contracts/`. Se agrega `pydantic` como dependencia.

### 2026-10-14 · T07 · merge de `codex/T01` a `main`
- Revisión de T01 (Claude): OK. `uv run pytest` 11 tests y `ruff check` sin errores en `main`.
- Nota para T32: `BedrockClient` no permite cambiar el modelo por llamada; el simulador con Haiku debe crear su propio cliente con `BedrockSettings(model_id="us.anthropic.claude-haiku-4-5")`.

### 2026-10-14 · T01 · `125f8f8`
- T01 implementada por Codex: configuración Python, estructura inicial y cliente Bedrock. `uv run pytest`: 11 tests pasan; ruff check y format OK. Documentación en [[T01-scaffold-python]].
