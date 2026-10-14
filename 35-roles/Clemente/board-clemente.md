---
tipo: board
integrante: Clemente
color: azul
entorno: Claude Code + Codex
frente: Agente e integración
---
# 🟦 Board de Clemente — Agente e integración

| | |
|---|---|
| **Entorno** | Claude Code + Codex |
| **Carpetas de código propias** | `src/contracts/`, `src/agent/`, `src/tools/`, `50-prompts/` |
| **Ramas** | `clemente/T<nn>-<descripcion>` |
| **Commits** | `T<nn>: <qué hiciste>` |
| **Bitácora** | [[bitacora-clemente]] |
| **Equipo, mapa y reglas** | [[_equipo]] · [[_avance]] |

Cómo se usa: mueve la línea de la tarea entre secciones. Marca `[x]` solo cuando se cumpla el criterio ✅ y la tarea esté en `main`.

## En curso
- 

## Por hacer
- [ ] **T03** · P0 · B1 · Herramienta `consultar_perfil(run)` sobre `perfiles.json`, aceptando RUN con o sin puntos (Codex) — ✅ tests: RUN existente, inexistente y con `rsh = null` · ~~depende de T02~~ desbloqueada: devolver `Profile` de `src.contracts`
- [ ] **T04** · P0 · B2 · Bucle del agente con Bedrock Converse + tool use, con límite de iteraciones y manejo de errores de herramientas ([[0003-orquestacion-agente]]) — ✅ `uv run agente --run <RUN>` devuelve ruta, hitos y checklist · depende de T03, T11 y T12
- [ ] **T05** · P0 · B2 · Prompt del sistema y especificación de herramientas: lenguaje claro, citar `fuente_url`, nunca inventar requisitos ni montos, presentar `elegible` como orientación preliminar y no consultar el perfil sin autorización — ✅ en `50-prompts/agente-pgu.md` y `src/agent/prompts.py`
- [ ] **T06** · P0 · B3 · Integración de punta a punta: agente real detrás de la API (con Jonmor) — ✅ 5 RUN, uno por cada estado, dan una ruta correcta desde la API · depende de T04, T16 y T21
- [ ] **T07** · P0 · B3–B4 · Revisión de PR (Claude), merges a `main` y congelamiento a las 09:30 del viernes — ✅ `main` siempre corre; bitácora del día al cierre

## Bloqueos
-

## Hecho
- [x] **T02** · P0 · B1 · (Claude) Contratos compartidos en `src/contracts/` (pydantic) — ✅ en `main`; 10 tests nuevos, los 500 perfiles del dataset cargan · [[T02-contratos]]
- [x] **T01** · P0 · B1 · Scaffold del repo: `pyproject.toml` con uv, ruff y pytest; estructura `src/`; cliente Bedrock que lee el modelo desde `.env` (Codex) — ✅ `uv run pytest` pasa en `main` (11 tests) · commit `125f8f8` · [[T01-scaffold-python]]
