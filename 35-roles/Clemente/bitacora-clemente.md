---
tipo: bitacora-integrante
integrante: Clemente
---
# Bitácora de Clemente

Una entrada por avance o commit relevante, la más reciente arriba. Así se puede seguir el historial de cada tarea sin leer todo `git log`.

Formato: `### AAAA-MM-DD HH:MM · T<nn> · <commit corto>` y debajo qué se hizo, qué falta y si algo bloquea a otro integrante.

### 2026-10-14 · T03 · rama `codex/T03`
- Consulta por RUN con/sin puntos, DV validado y retorno `Profile`; `None` si no existe. Permisos mediante `Case.can_read_profile` y coincidencia del RUN antes de leer el archivo.
- Dataset cargado una vez por repositorio y respuestas copiadas; conserva RSH ausente. Suite: 40 tests pasan, 19 nuevos. Guía [[T03-consultar-perfil]].
- Lista para revisión/integración T07. El commit usa `T03: consultar perfiles con autorización y RUN normalizado` y registra esta entrada.

### 2026-10-14 · T02 · rama `clemente/T02-contratos`
- Contratos compartidos en `src/contracts/` (perfil, evaluación PGU, hitos, caso con invitación, autorización, ruta, checklist y mensajes). Se agrega `pydantic` como dependencia.
- `uv run pytest`: 21 tests (10 nuevos); `ruff check` sin errores. Los 500 perfiles de `perfiles.json` cargan con `Profile.model_validate`.
- Desbloquea T03 (Codex), T11 y T12 (Johann), T15, T16 y T21 (Jonmor), y los mocks de Bruno. Guía en [[T02-contratos]].

### 2026-10-14 · T07 · merge de `codex/T01` a `main`
- Revisión de T01 (Claude): OK. `uv run pytest` 11 tests y `ruff check` sin errores en `main`.
- Nota para T32: `BedrockClient` no permite cambiar el modelo por llamada; el simulador con Haiku debe crear su propio cliente con `BedrockSettings(model_id="us.anthropic.claude-haiku-4-5")`.

### 2026-10-14 · T01 · `125f8f8`
- T01 implementada por Codex: configuración Python, estructura inicial y cliente Bedrock. `uv run pytest`: 11 tests pasan; ruff check y format OK. Documentación en [[T01-scaffold-python]].
