---
tipo: implementacion
tarea: T04
dueño: Clemente (Claude)
fecha: 2026-10-14
---
# T04 — Bucle del agente (Bedrock Converse + tool use)

Implementa [[0003-orquestacion-agente]] sobre [[T02-contratos]], [[T03-consultar-perfil]] y [[agente-pgu]]. Estado en [[board-clemente]].

```
uv run agente --run 100.000.010-4                      # chat en la terminal
uv run agente --run 100000010-4 --mensaje "¿Me corresponde la PGU?"
```

La CLI **simula** una invitación aceptada y una autorización otorgada, solo para la demo. En el producto ambas vienen del flujo de la API (T21).

## Piezas
| Archivo | Qué hace |
|---|---|
| `src/agent/loop.py` | `Agent.run_turn(case, texto, channel=...)`: guarda el mensaje, llama a Converse, ejecuta herramientas y repite hasta `end_turn` o `max_iterations` (6). Si llega al límite, responde con un mensaje seguro. |
| `src/agent/tools.py` | `build_registry()`: registra **solo** las herramientas con implementación. Formato común de resultado: `{"ok": true, "data": ...}` o `{"ok": false, "error": {"type", "message"}}`. |
| `src/agent/route.py` | `build_route(result, milestones)`: arma la ruta y el checklist **en código** a partir del resultado PGU. |
| `src/agent/cli.py` | Comando `agente`. |

## Decisiones
- **Contexto de confianza en el prompt**: en cada turno se agrega al prompt del sistema un bloque con el canal, la fecha de referencia, el RUN, la invitación, si el acceso está autorizado y la evaluación previa. Lo entrega la aplicación, no la persona.
- **Historial entre canales**: los mensajes del caso se convierten en turnos de Converse. Lo que viene de otro canal o del ejecutivo se marca como `[ejecutivo · sucursal]`, para que el agente sepa qué pasó en sucursal.
- **Errores de herramienta**: `PermissionError` → `permission_denied`, `ValueError` → `invalid_input`, sin perfil → `not_found`, herramienta inexistente → `unknown_tool`. Cualquier otro error → `internal`, sin detalles. El modelo recibe el error como `toolResult` con `status: error` y la conversación sigue.
- **Las reglas de Johann se conectan solas**: si `src/rules` exporta `evaluar_pgu(profile, fecha_ref) -> PguResult` y `calcular_hitos(profile, fecha_ref) -> list[Milestone]`, se registran sin tocar el agente. Hasta entonces, el agente solo ofrece `consultar_perfil` y `leer_caso`.
- **Las herramientas guardan en el caso**: `evaluar_pgu` y `calcular_hitos` escriben `pgu_result` y `milestones`, y regeneran la ruta y el checklist. El LLM no escribe el caso. `guardar_caso` no se registra hasta que exista el repositorio de casos (T15).
- **Ruta provisoria**: los textos de la ruta son orientación general. Todas las fuentes aparecen como `verified=False` hasta que T09 entregue la ficha oficial. Cuando exista el catálogo (T14), `build_route` debe tomar los pasos de ahí.

## Verificación
- `uv run pytest`: 57 tests (11 nuevos de T04) con un cliente Converse falso, sin llamar a AWS. Cubren: herramienta y respuesta, falta de autorización, RUN ajeno, herramienta inexistente, límite de iteraciones, herramientas ofrecidas, reglas que llenan el caso, contexto del prompt, historial entre canales y antecedentes faltantes.
- Prueba real con Bedrock (Sonnet 5, 14-10-2026) con el RUN `100000010-4`: llamó a `consultar_perfil` y `leer_caso`, citó el dataset como fuente y se negó a afirmar que la PGU corresponde sin una evaluación.

## Pendientes
- **Ajustar el prompt (T05)**: sin `evaluar_pgu`, el modelo igual explicó de memoria los requisitos generales de la PGU y el número 101. Hay que reforzar que, sin una herramienta, solo diga que falta la evaluación.
- Conectar `evaluar_pgu` y `calcular_hitos` cuando lleguen T11 y T12; `buscar_beneficios` con T14; `guardar_caso` con T15.
- Aceptar un RUN sin guion en `normalize_run` (T03).
