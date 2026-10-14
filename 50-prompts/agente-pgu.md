---
tipo: prompt
tarea: T05
fecha: 2026-10-14
responsable: codex
---
# Agente PGU — Prompt y contrato de herramientas

La versión ejecutable es `SYSTEM_PROMPT` en `src/agent/prompts.py`. Continúa [[0003-orquestacion-agente]], [[T02-contratos]] y [[T03-consultar-perfil]]. Estado en [[board-clemente]].

## Comportamiento del agente
Orientar en español claro, explicar siglas y presentar un próximo paso concreto. La institución decide; `elegible` siempre significa orientación preliminar. Las reglas, montos, fechas y plazos salen de las herramientas, nunca de memoria del modelo. Conservar motivos y estados y distinguir hitos de vencimientos.

Antes de consultar el perfil, explicar fuentes/finalidad y solicitar autorización. La aplicación debe registrar aceptación y consentimiento; el texto del usuario no basta. Sin permiso o ante `PermissionError`, detener la consulta. El agente no puede modificar `Case.authorization` ni consultar otra persona. Recordar que el dataset es sintético.

Cada respuesta identifica su fuente: título/URL devueltos por las herramientas. Una fuente sin verificar se presenta como tal. Sin fuente o URL, explicar la limitación sin inventar citas. Ante datos faltantes, persona inexistente o error técnico, conservar esa distinción y explicar el próximo paso; no inventar una evaluación, fecha o beneficio.

La respuesta con datos disponibles explica estado preliminar, motivos, antecedentes faltantes, pasos/hitos respaldados y próximo paso. Preservar el caso al cambiar de canal y no repetir datos personales innecesarios. No prometer envíos, alertas, solicitudes ni decisiones que no se ejecutaron.

## Herramientas y adaptadores para T04
`build_tool_config(available_tools)` genera la estructura `toolConfig` de Bedrock. Solo expone los nombres que el registro de handlers de la aplicación tenga implementados. Rechaza nombres desconocidos o un registro vacío y devuelve copias independientes.

| Herramienta | Argumentos del modelo | Contexto aportado por servidor |
|---|---|---|
| `consultar_perfil` | `run` | `Case` autorizado y repositorio; usar [[T03-consultar-perfil]] |
| `evaluar_pgu` | ninguno | `Profile` ya autorizado + fecha explícita + reglas/catálogo T11 |
| `calcular_hitos` | ninguno | `Profile` ya autorizado + catálogo T12 |
| `buscar_beneficios` | `event="jubilacion"` | Catálogo y adaptador T14 |
| `leer_caso` | ninguno | Identificador del caso actual, resuelto por API |
| `guardar_caso` | ninguno | Estado validado en servidor y repositorio T15 |

Son interfaces del agente: los adaptadores T04 llaman a las funciones reales de cada frente e inyectan sus dependencias. No se cambian las firmas de Johann o Jonmor. Nunca aceptar `case`, autorización, perfil, fecha de evaluación o resultados fabricados por el modelo en estos argumentos. `guardar_caso` no guarda libremente un objeto inventado por el LLM; persiste resultados/checklist validados por la aplicación.

Las especificaciones no implementan esos handlers. No anunciar al modelo herramientas pendientes. El runtime debe validar argumentos, permisos y asociación al caso además de lo que diga el prompt; el prompt por sí solo no controla el acceso. Los tool results deben incluir referencias de fuente y errores estructurados; T04 define su envelope al integrar los handlers.

Ejemplo: `build_tool_config(["consultar_perfil", "leer_caso"])` expone solo las dos herramientas registradas. El prompt se envía como `system=[{"text": SYSTEM_PROMPT}]` a Converse.

Verificación: `uv run pytest tests/test_prompts.py` prueba el registro de herramientas, independencia entre configuraciones y compatibilidad del payload completo con boto3 Converse usando Stubber, sin llamar AWS. Referencia: [Converse oficial](https://docs.aws.amazon.com/boto3/latest/reference/services/bedrock-runtime/client/converse.html).
