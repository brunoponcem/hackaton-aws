---
tipo: revision
fecha: 2026-10-14
aporte: 0d06dab
merge-remoto: ed989ad
responsable: codex
---
# Revisión e integración del aporte de Johann

El aporte `0d06dab`, rama `johann/app-mvp-ruta-pgu`, ya estaba integrado en `origin/main` mediante PR #1 (`ed989ad`). Se hizo fetch y merge por avance directo en el checkout local, sin conflictos textuales y conservando las notas locales. El código vive en `src/app`. Contexto actualizado en [[contexto-codear-johann]].

## Qué aporta

App Streamlit con invitación, autorización, situación previsional, ruta/checklist, asistente, vista de ejecutivo, campañas simuladas y medición. SQLite conserva invitación, permisos, pasos e historial por canal. Motor determinista de jubilación/PGU, fechas, dependencias de pasos, asistente por plantillas y Bedrock opcional. Lee los 500 perfiles sintéticos del dataset A.

Es un MVP autónomo funcional, no todavía la unificación con `src/contracts`, `src/tools` y `src/agent`. No trae API FastAPI ni la escalera email/llamada/trabajo/terreno o heatmap del ADR 0005; la campaña actual registra invitaciones simuladas.

## Correcciones de integración

- Grupo uv `app` con las versiones de Streamlit/pandas del aporte; lock actualizado y `src/app` como paquete importable. boto3 conserva la versión del entorno compartido. README con arranque desde la raíz; no mezclar su `requirements.txt` autónomo con la `.venv` común.
- Sin autorización, el asistente responde por plantilla y no envía el historial previo a Bedrock. Ambas vistas reinician el chat al retirar autorización, para que no siga mostrando respuestas sensibles anteriores.
- El repositorio SQLite exige invitación aceptada antes de otorgar autorización. Rechazar la invitación revoca consentimiento previo; reabrir exige autorizar de nuevo.
- `verificar.py` fuerza modo offline aunque exista `BEDROCK_MODEL_ID` en el proceso; sus miles de consultas no consumen inferencias inadvertidamente.

## Evidencia ejecutada

- `uv run --group app pytest`: **61 tests pasan** (57 previos + 4 de integración).
- `uv run --group app python src/app/verificar.py`: **TODO OK**, fechas límite, dependencias, seguimiento SQLite y consultas por plantillas sobre 500 perfiles.
- AppTest de Streamlit ejecuta la vista inicial y el flujo aceptar → autorizar → preguntar → revocar sin excepciones; verifica que desaparezca el historial anterior. No se hizo una revisión visual en navegador ni una llamada Bedrock real.
- Ruff pasa en los tests nuevos. El lint completo de `src/app` falló en el aporte original con **190 observaciones**, mayormente longitud/formato/imports y dos lambdas asignadas. No se reformateó en bloque el aporte para evitar mezclar una reescritura extensa con el merge funcional. El lint global no se presenta como aprobado.

Conteos del motor al 2026-10-08: `futuro=405`, `proximo=14`, `excluido=20`, `elegible=26`, `no_elegible=26`, `antecedente_faltante=9`. No son concesiones de PGU ni conteos institucionales. Los 37 candidatos de la nota inicial eran una aproximación sin pensión base; no se fuerza el motor a reproducirlos. No hay PGU vigente según el verificador del aporte; las dos personas destacadas tienen registros suspendidos.

## Diferencias y límites por resolver

| Hallazgo | Efecto en la integración |
|---|---|
| Dataclasses/dicts propios frente a modelos pydantic comunes | No conectar directamente sus resultados al `Case` existente; falta adaptar y decidir la implementación única |
| Estados extra `futuro` y `excluido` | No pertenecen a `PguStatus`; no mapearlos a otro estado sin definir semántica |
| SQLite por RUN y eventos frente a caso/mensajes del agente | El asistente Streamlit y el agente CLI siguen teniendo repositorios/historiales separados; el historial del chat vive en sesión y SQLite registra preguntas, no todas las respuestas |
| Segundo cliente Bedrock | No reutiliza `BedrockClient` ni su allowlist, y lee variables del proceso sin cargar automáticamente `.env`; integración pendiente |
| Evaluación completa cacheada antes de consentimiento | La app demo procesa perfiles sintéticos por lotes; no confundirlo con una consulta ciudadana real autorizada de registros del Estado |
| Parámetros sin tabla de vigencias/consulta por valor | No afirmar validación normativa completa; resolver antes de uso real o fechas distintas de la demo |
| Pensión base simplificada | El código suma pensiones vigentes si existen; solo usa PAFE si no hay pensiones. Revisar la combinación de PAFE, sobrevivencia y otros regímenes; no declarar la fórmula oficial implementada |

Contraste de fuentes: la [Superintendencia de Pensiones](https://www.spensiones.cl/portal/institucional/594/w3-article-15170.html) describe la pensión base como combinación de PAFE y otras pensiones según régimen. Su [comunicado de reajuste 2026](https://www.spensiones.cl/portal/institucional/594/w3-article-16886.html) respalda los parámetros de $231.732, pensión inferior $789.139 y superior $1.252.602. Esa corroboración parcial no verifica toda la lógica del prototipo ni sus proyecciones. Las fichas de ChileAtiende consultadas directamente devolvieron 403 en esta revisión.

La app corre como demo local sin login. No se despliega como servicio público desde esta revisión. Los aportes se conservan; las diferencias semánticas anteriores se dejan explícitas en vez de eliminar código o cambiar estados solo para que encajen.

## Ejecutar

```powershell
uv sync --group app
uv run --group app pytest
uv run --group app python src/app/verificar.py
uv run --group app streamlit run src/app/app.py --server.address localhost
```

Los tests de UI requieren el grupo `app`; sin él se omite únicamente esa prueba. Leer [[inicio-kiro-johann]] para el contexto acotado de Johann.
