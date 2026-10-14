# Tablero

Formato: `- [ ] tarea — dueño: humano|claude|codex — criterio de aceptación`

Reto: [[ChileAtiende-a-tiempo]] · Arquitectura: [[arquitectura-chileatiende]] · Datos: [[datos-dataset-A]]

Contexto de entrada para ambos agentes y presentación institucional: [[contexto-compartido-chileatiende]].

**Foco del MVP: jubilación + PGU** ([[0004-mvp-jubilacion-pgu]]).

## Por hacer
### Datos
- [ ] Preguntar a los mentores: ¿habrá dataset B?, ¿cómo se evalúa el uso de los datos?, ¿hay Amazon Connect? — dueño: humano — respuestas anotadas en [[datos-dataset-A]]
- [ ] Parámetros PGU (montos y umbrales vigentes) desde la ficha ChileAtiende → `data/catalogo/pgu.json` — dueño: humano + claude — cada valor con `fuente_url`
- [ ] Definir el esquema del catálogo (`data/catalogo/schema.json`) — dueño: claude — esquema + `pgu.json` que valide
- [ ] Catálogo de otros beneficios de jubilación (solicitud de pensión, bono por hijo) — dueño: codex — valida contra el esquema

### Backend
- [ ] Scaffold de `src/` (uv, ruff, pytest, cliente Bedrock con el modelo desde `.env`) — dueño: codex — `uv run pytest` pasa
- [ ] Herramienta `consultar_perfil(run)` sobre `perfiles.json` — dueño: codex — tests: RUN existente, RUN inexistente, perfil con `rsh = null`
- [ ] Herramienta `evaluar_pgu(perfil, fecha_ref)` → `elegible | no_elegible | antecedente_faltante | proximo | ya_recibe` + motivos — dueño: codex — tests con un perfil real del dataset por cada resultado
- [ ] Script de evaluación por lotes de los 500 perfiles → `reports/pgu_dataset_A.csv` + resumen — dueño: codex — cuadra con los conteos de [[datos-dataset-A]] o explica la diferencia
- [ ] Herramienta `calcular_plazos` (aviso antes de los 65, vigencia del RSH) — dueño: codex — tests con fechas límite
- [ ] Herramienta `buscar_beneficios` (búsqueda simple sobre el catálogo) — dueño: codex — el test devuelve los beneficios correctos por evento
- [ ] Bucle del agente con Converse + tool use ([[0003-orquestacion-agente]]) — dueño: claude — una CLI local recibe un RUN y arma la ruta PGU citando fuentes
- [ ] Repositorio de casos (interfaz + memoria + DynamoDB) — dueño: codex — tests con la implementación en memoria
- [ ] API FastAPI (`/cases`, `/cases/{id}/messages`, `GET /cases/{id}`) — dueño: codex — test de integración con un agente falso

### Producto y demo
- [ ] Diseñar aceptación/rechazo de invitación, autorización de datos y checklist del caso — dueño: claude — contratos y flujo documentados según [[contexto-compartido-chileatiende]]
- [ ] Verificar hitos oficiales: jubilación por perfil y solicitud PGU desde 64 años y 9 meses — dueño: humano + claude — fuentes, vigencias y reglas documentadas antes de implementar
- [ ] Definir medición de próximo paso, comprensión y continuidad — dueño: humano + claude — denominadores y evidencia definidos; metas del PPT separadas de resultados simulados
- [ ] Frontend: chat de la persona + panel del ejecutivo — dueño: claude — ambas vistas muestran el mismo caso en vivo
- [ ] Simulador de usuarios con Haiku 4.5 (a partir de perfiles del dataset) + métricas — dueño: claude — reporte con % de rutas completas sobre N personas
- [ ] Despliegue en AWS con CDK (Lambda + API Gateway + DynamoDB) — dueño: codex — `cdk deploy` OK y URL pública (opcional)
- [ ] Guion del pitch y de la demo — dueño: humano — listo el viernes antes de las 10:15

## En curso

## Hecho
- [x] Agregar pipeline del MVP al contexto compartido — dueño: codex — diagrama Mermaid, flujo técnico y ejemplo de demo en [[contexto-compartido-chileatiende]]
- [x] Revisar trabajo de Claude y extraer presentación a contexto compartido — dueño: codex — [[contexto-compartido-chileatiende]] y `scripts/extract-ppt-context.ps1` verificado sobre 7 diapositivas
- [x] Estructura del repo — dueño: claude
- [x] Elegir reto con [[_seleccion]] — dueño: humano — ChileAtiende a tiempo ([[0002-seleccion-reto]])
- [x] Verificar acceso a cuenta AWS y Bedrock — dueño: humano — perfil `hackaton`, us-east-1, Sonnet 5 / Opus 5 / Haiku 4.5
- [x] Revisar dataset A y documentarlo — dueño: claude — [[datos-dataset-A]]
- [x] Versionar `data/raw/` en git — dueño: humano — dataset A commiteado
- [x] Aprobar [[arquitectura-chileatiende]], [[0003-orquestacion-agente]] y [[0004-mvp-jubilacion-pgu]] — dueño: humano — ADR aceptados
- [x] Adaptar [[arquitectura-base]] al reto — dueño: claude — [[arquitectura-chileatiende]] + ADR 0002 y 0003
