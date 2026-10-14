# AGENTS.md — Reglas compartidas (Claude Code + Codex)

Este archivo es la **fuente única de verdad** para cualquier agente de IA que trabaje en el repo.
Codex lo lee automáticamente; Claude Code lo importa desde `CLAUDE.md`.

## Contexto
- Lectura de entrada para ambos agentes: [[contexto-compartido-chileatiende]] (presentación institucional, decisiones, estado comprobado y pendientes); después revisar [[board]] y la bitácora vigente.
- Hackatón AWS, Chile, octubre 2026. Tiempo limitado: priorizar demo funcional sobre perfección.
- **Reto elegido: [[ChileAtiende-a-tiempo]]**: ruta de beneficios y plazos por evento de vida, con continuidad entre canales. Arquitectura en [[arquitectura-chileatiende]].
- **Idea central desde el 14-10** ([[0005-asistente-contacto-escalonado]]): asistente frontal estilo ChileAtiende; contacto escalonado email → llamada → trabajo → puerta a puerta (solo se escala si no hay respuesta; declinar detiene todo); campañas por heatmap; acompañamiento hasta la derivación al ejecutivo; ficha clara para ejecutivos y trabajadores sociales. Diseño en [[contacto-y-campanas]].
- Cuenta AWS del evento: perfil `hackaton`, región `us-east-1`. Modelos Bedrock permitidos: `us.anthropic.claude-sonnet-5` (por defecto), `us.anthropic.claude-opus-5` y `us.anthropic.claude-haiku-4-5`. Los modelos `*-5-5` y Fable están bloqueados.
- Regla del dominio: la elegibilidad y los plazos se calculan en código, nunca los inventa el LLM, y toda respuesta cita su fuente.
- El repo es también un **vault de Obsidian**: las notas `.md` son documentación viva.
- Idioma: notas y commits en español; código e identificadores en inglés.

## Dónde está cada cosa
| Carpeta | Contenido |
|---|---|
| `00-inbox/` | Ideas sueltas, capturas rápidas |
| `10-retos/` | Una nota por reto del hackatón + `_seleccion.md` con la matriz de decisión |
| `20-arquitectura/` | Arquitectura objetivo y `adr/` (decisiones registradas) |
| `30-tareas/` | `board.md`: tablero de tareas con dueño (humano / claude / codex) |
| `35-roles/` | Una carpeta por integrante con su `board-<nombre>.md` y `bitacora-<nombre>.md`; `_equipo.md` (plan, mapa del pipeline, reglas) y `_avance.md` (todos los boards en una vista) |
| `40-bitacora/` | Una nota diaria con lo que pasó |
| `50-prompts/` | Prompts reutilizables y roles de agentes |
| `src/` | Código de la aplicación |
| `infra/` | IaC (AWS CDK o SAM) |
| `scripts/` | Utilidades (chequeo de entorno, deploy) |

## Reparto de trabajo entre agentes
- **Claude Code**: arquitectura, diseño de módulos, refactors grandes, revisión de PRs, documentación en el vault.
- **Codex**: implementación de tareas acotadas, tests, scripts, fixes puntuales.
- Nunca dos agentes sobre los mismos archivos a la vez. Usar ramas `claude/<tarea>` y `codex/<tarea>` (o git worktrees).
- Antes de empezar una tarea: marcarla en `30-tareas/board.md` con tu nombre.
- Al terminar: actualizar la nota de bitácora del día y, si tomaste una decisión de diseño, crear un ADR en `20-arquitectura/adr/`.

## Convenciones de código
- Python 3.12, `uv` para dependencias, `ruff` para lint/format, `pytest` para tests.
- Infra en AWS CDK (Python) dentro de `infra/`. Región por defecto `us-east-1` salvo que la organización indique otra.
- IA en AWS: preferir **Amazon Bedrock** (modelos Claude vía Bedrock) para LLM; S3 para datos; Lambda/ECS para cómputo.
- Nada de credenciales en el repo. Usar `aws configure sso` o variables de entorno; `.env` está en `.gitignore`.
- Cada PR: descripción corta, cómo probarlo, y qué falta.

## Definición de "terminado"
1. Corre localmente (`uv run ...` o `make dev`).
2. Tiene al menos un test o un script de verificación.
3. Está documentado en una nota del vault (enlazada con `[[...]]`).
