---
tipo: bitacora-integrante
integrante: Clemente
---
# Bitácora de Clemente

Una entrada por avance o commit relevante, la más reciente arriba. Así se puede seguir el historial de cada tarea sin leer todo `git log`.

Formato: `### AAAA-MM-DD HH:MM · T<nn> · <commit corto>` y debajo qué se hizo, qué falta y si algo bloquea a otro integrante.

### 2026-10-15 · Direcciones individuales simuladas · `643a888`
- A pedido del usuario: calor desde una ubicación ficticia por persona, con núcleos y dispersión dentro del polígono comunal. Misma paleta/fondo RM; desaparecen los círculos comunales ponderados. Puntos inspeccionables, etiquetas comunales opcionales y detalle Barrios/Sectores amplios.
- Dirección rotulada SIMULADA, coordenadas a seis decimales y procedencia sintética; no son domicilios RSH ni calles verificadas. Nuevos contactos persisten ubicación; snapshots anteriores se enriquecen determinísticamente sin reescribir casos. Umbral comunal de cinco conservado.
- 113 tests pasan (14 nuevos), ruff y verificador TODO OK. Chrome muestra calor y puntos con 84 ubicaciones para los 84 casos publicables, sin excepciones ni solicitudes de mapa fallidas. [[0010-direcciones-simuladas]] · [[heatmap-campanas-simulado]].

### 2026-10-15 · Rediseño metropolitano · `475100e`
- A pedido del usuario: solo Región Metropolitana, calles vectoriales oscuras CARTO/OSM, contornos de 52 comunas BCN, calor 2048, etiquetas exactas y colores fijos por conteo. Ocho comunas sintéticas en nuevas inicializaciones, sin alterar canales ni casos previos. Base independiente `funnel-demo-rm.db`.
- Ranking y propuesta por comuna; umbral mínimo de 5 ahora comunal. Escenario precargado sin respuestas: 92 casos, 84 publicables en seis comunas. Los restantes grupos se omiten, sin inventar personas ni domicilios. Fondo urbano requiere internet.
- 99 tests pasan (9 nuevos), ruff check/format OK y verificador de 500 perfiles TODO OK. Chrome comprobado a doble densidad en 1440/1024 px, sin excepciones; todos los focos y etiquetas entran en pantalla. [[heatmap-campanas-simulado]] · [[0009-heatmap-metropolitano]].

### 2026-10-15 · Heatmap y campañas simuladas · `b4d517f`
- Mapa para ejecutivos en laboratorio localhost:8502 y Detectar e invitar; cola presencial, diagnóstico de activos, filtro regional, ranking determinista y propuesta de jornadas por capacidad. Grupos menores de 5 se suprimen antes de frontend y exportación. No hay agenda ni despacho.
- RSH del evento sin comuna/provincia; usa seis territorios de la capa sintética. Contornos Natural Earth locales, sin solicitudes remotas de mapa verificadas en Chrome. No son domicilios ni centroides oficiales.
- 90 tests pasan, ruff OK y verificador de 500 perfiles TODO OK. [[heatmap-campanas-simulado]] · [[0008-heatmap-campanas-sinteticas]]. Siguen pendientes datos autorizados, campañas reales, alertas/CESFAM y acompañamiento.

### 2026-10-15 · Backend del embudo · `7d1d8e0`
- Revisados los pendientes actuales y [[contacto-y-campanas]]. Implementados contactos sintéticos, backend persistente con reloj, simulación reproducible y embudo visual. Escala solo si no inició trámite; declinar detiene todo. No hay envíos/calls/visitas reales.
- CLI `scripts/colador_backend.py`, laboratorio `src/app/demo_embudo.py` en localhost:8502 y componente compartido en Detectar e invitar. La demo usa una base separada y permite conservar escenarios.
- 84 tests pasan (20 nuevos), ruff de módulos nuevos OK y verificador de 500 perfiles TODO OK. Chrome muestra gráfico/tablas sin excepciones. Guía [[backend-embudo-contacto]] y [[0007-backend-embudo-simulado]].
- Quedan heatmap, alerta/CESFAM, envíos reales y acompañamiento ampliado, sin marcarlos como implementados.

### 2026-10-14 · T04 · rama `clemente/T04-agente`
- Agente con Converse + tool use: límite de iteraciones, formato común de errores, contexto del caso en el prompt e historial entre canales. Ruta y checklist deterministas. CLI `uv run agente --run <RUN>`. Guía en [[T04-agente]].
- 57 tests (11 nuevos) y ruff OK. Prueba real con Bedrock Sonnet 5 y el RUN `100000010-4`: consulta el perfil, cita el dataset y no adjudica la PGU.
- Falta: conectar T11 y T12 de Johann (se registran solas desde `src/rules`). Ajustar el prompt, porque sin `evaluar_pgu` el modelo igual explica requisitos de memoria.

### 2026-10-14 · T07 · merge de T03 y T05 a `main` (`36cd846`)
- Revisión (Claude): aprobadas. 46 tests, `ruff check` y `ruff format --check` OK. El DV módulo 11 es correcto, la autorización se valida antes de leer el archivo y no se puede consultar otro RUN que el del caso.
- Pendientes para T04, no bloqueantes:
  - `guardar_caso` no tiene parámetros: T04 debe definir qué guarda (ruta, checklist) y validarlo contra `RouteStep` y `ChecklistItem`.
  - El prompt no incluye el contexto dinámico del caso (estado de la autorización, canal, fecha de referencia): T04 lo inyecta en cada turno.
  - `normalize_run` rechaza un RUN sin guion (`1000000015`), que es habitual al escribirlo. Conviene aceptarlo.

### 2026-10-14 · T05 · rama `codex/T05`
- Prompt ejecutable y [[agente-pgu]]: orientación preliminar, fuentes, consentimiento registrado por la aplicación, conservación de estados y separación entre hitos/vencimientos.
- Especificaciones Converse para adaptadores del caso actual; solo se exponen handlers registrados. Casos/perfiles/fechas vienen del servidor, no del LLM. Los handlers de otros frentes siguen pendientes; no se anuncian como implementados.
- Suite: 46 tests pasan, ruff check y format OK. Lista para revisión/integración T07. Commit `T05: definir prompt PGU y especificaciones de herramientas` registra esta entrada.

### 2026-10-14 · T03 · `6ea8da0` (rama `codex/T03`)
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
