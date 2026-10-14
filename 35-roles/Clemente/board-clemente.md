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
- [ ] **T05** · P0 · B2 · (Codex, `codex/T05`) Implementada y lista para revisión: prompt y especificación de herramientas — suite 46 tests OK; pendiente integración T07 · [[agente-pgu]]
- [ ] **T03** · P0 · B1 · (Codex, `codex/T03`) Implementada y lista para revisión: consultar RUN y devolver `Profile` con autorización — 40 tests OK (19 nuevos); pendiente integración T07 · [[T03-consultar-perfil]]

## Por hacer
- [ ] **T04** · P0 · B2 · Bucle del agente con Bedrock Converse + tool use, con límite de iteraciones y manejo de errores de herramientas ([[0003-orquestacion-agente]]) — ✅ `uv run agente --run <RUN>` devuelve ruta, hitos y checklist · depende de T03, T11 y T12
- [ ] **T06** · P0 · B3 · Integración de punta a punta: agente real detrás de la API (con Jonmor) — ✅ 5 RUN, uno por cada estado, dan una ruta correcta desde la API · depende de T04, T16 y T21
- [ ] **T07** · P0 · B3–B4 · Revisión de PR (Claude), merges a `main` y congelamiento a las 09:30 del viernes — ✅ `main` siempre corre; bitácora del día al cierre

## Bloqueos
- T04 depende de las reglas/hitos de Johann (T11 y T12), todavía ausentes en el `main` observado. T06 requiere además API y flujo autorizado T16/T21. T03 y T05 están listas en ramas aisladas para revisión T07.

## Hecho
- [x] **T02** · P0 · B1 · (Claude) Contratos compartidos en `src/contracts/` (pydantic) — ✅ en `main`; 10 tests nuevos, los 500 perfiles del dataset cargan · [[T02-contratos]]
- [x] **T01** · P0 · B1 · Scaffold del repo: `pyproject.toml` con uv, ruff y pytest; estructura `src/`; cliente Bedrock que lee el modelo desde `.env` (Codex) — ✅ `uv run pytest` pasa en `main` (11 tests) · commit `125f8f8` · [[T01-scaffold-python]]
