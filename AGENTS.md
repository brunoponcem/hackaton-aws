# AGENTS.md — Reglas compartidas (Claude Code + Codex)

Este archivo es la **fuente única de verdad** para cualquier agente de IA que trabaje en el repo.
Codex lo lee automáticamente; Claude Code lo importa desde `CLAUDE.md`.

## Contexto
- **Al iniciar cada sesión, leer en este orden** (siempre desde el disco, porque cambian seguido; no confiar en una lectura anterior):
  1. `35-roles/_equipo.md`: equipo, forma de trabajo y estado del pipeline.
  2. **El board del integrante para quien trabajas**: `35-roles/<Nombre>/board-<nombre>.md`. En el checkout de Clemente, Claude y Codex trabajan para Clemente: `35-roles/Clemente/board-clemente.md`. **Sus pendientes son la lista de trabajo.**
  3. Las notas de diseño que enlace cada pendiente (por ejemplo, [[contacto-y-campanas]]) y la arquitectura vigente ([[arquitectura-chileatiende]]).
  4. La bitácora del integrante (`35-roles/<Nombre>/bitacora-<nombre>.md`) y la del día en `40-bitacora/`.
  5. [[contexto-compartido-chileatiende]] como contexto institucional (PPT, KPI).
- Si un pendiente no tiene suficiente detalle para implementarlo, buscar la nota de diseño enlazada; si no existe, preguntar antes de inventar el alcance.
- Hackatón AWS, Chile, octubre 2026. Tiempo limitado: priorizar demo funcional sobre perfección.
- **Reto elegido: [[ChileAtiende-a-tiempo]]**: ruta de beneficios y plazos por evento de vida, con continuidad entre canales. Arquitectura en [[arquitectura-chileatiende]].
- **Idea central desde el 14-10** ([[0005-asistente-contacto-escalonado]]): asistente frontal estilo ChileAtiende; **colador de contacto** de lo general a lo específico: email automático a todos → llamada → trabajo → asistencia presencial con mapeo de residencia. Pasa a la etapa siguiente quien **no inició su trámite**; declinar detiene todo. Heatmap por provincia de quienes no respondieron, para campañas localizadas, y **alerta de beneficio nivel máximo** al ingresar su RUN en ChileAtiende o en un CESFAM (en el CESFAM, solo un mensaje mínimo). Acompañamiento hasta la derivación al ejecutivo y ficha clara para ejecutivos y trabajadores sociales. Diseño en [[contacto-y-campanas]].
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
| `30-tareas/` | `board.md`: tablero histórico del reparto inicial; **ya no es la lista de trabajo** |
| `35-roles/` | **Lista de trabajo vigente.** `_equipo.md` (equipo, forma de trabajo, pipeline coloreado por estado), `_avance.md` (boards en una vista) y una carpeta por integrante (Clemente, Johann, Jonmor, Bruno, Jp) con `board-<nombre>.md` (pendientes) y `bitacora-<nombre>.md` |
| `40-bitacora/` | Una nota diaria con lo que pasó |
| `50-prompts/` | Prompts reutilizables y roles de agentes |
| `src/` | Código de la aplicación |
| `infra/` | IaC (AWS CDK o SAM) |
| `scripts/` | Utilidades (chequeo de entorno, deploy) |

## Reparto de trabajo entre agentes
- **Flujo vigente del código (acordado con el usuario):** Clemente trabaja con Codex + Claude y Johann con Kiro, actualmente desde `src/app`. No se asignan tareas ni carpetas exclusivas; se permiten aportes que se superpongan. Guardar cada aporte en commit, traer `origin/main`, integrar mediante merge, resolver conflictos y revisar duplicaciones funcionales, ejecutar las verificaciones aplicables y hacer push. Si el remoto avanzó, repetir la integración. Esta regla sustituye el reparto y la prohibición de solapamientos que se describen abajo para el código; las reglas de dominio y protección de credenciales siguen vigentes. Git no detecta automáticamente toda duplicación o incompatibilidad lógica.
- **Claude Code**: arquitectura, diseño de módulos, refactors grandes, revisión de PRs, documentación en el vault.
- **Codex**: implementación de tareas acotadas, tests, scripts, fixes puntuales.
- Nunca dos agentes sobre los mismos archivos a la vez. Usar ramas `claude/<tarea>` y `codex/<tarea>` (o git worktrees).
- Antes de empezar un pendiente: moverlo a "En curso" en el board del integrante (`35-roles/<Nombre>/board-<nombre>.md`).
- Al terminar: moverlo a "Hecho" con el commit; agregar una entrada en la bitácora del integrante y en la del día; si tomaste una decisión de diseño, crear un ADR en `20-arquitectura/adr/` y actualizar el estado del pipeline en `35-roles/_equipo.md`.
- Si el usuario agrega o cambia pendientes, el board manda sobre cualquier lista anterior (incluido `30-tareas/board.md`).

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
