---
tipo: reto
area: Gobierno digital
organizacion: ChileAtiende (IPS)
estado: elegido
fecha-eleccion: 2026-10-14
---
# ChileAtiende a tiempo — acompañamiento por evento de vida

> **Reto elegido** el 2026-10-14. Ver [[0002-seleccion-reto]] y [[arquitectura-chileatiende]].
> **Foco del MVP: jubilación + PGU**, con el dataset entregado por la organización ([[datos-dataset-A]], [[0004-mvp-jubilacion-pgu]]).

## Problema
A partir de un evento de vida (nacimiento, cesantía, jubilación), construir una ruta de beneficios, plazos y pasos que mantenga la continuidad entre canales (web, teléfono, sucursal, WhatsApp).

Hoy la persona tiene que saber qué preguntar. Si no conoce un beneficio o se le pasa un plazo, lo pierde. Además, cada canal empieza de cero.

## Propuesta de valor
- **Proactivo**: la persona cuenta qué le pasó y el sistema le devuelve qué le corresponde, hasta cuándo y en qué orden.
- **A tiempo**: plazos calculados desde la fecha del evento, con alertas antes de que venzan.
- **Continuo**: un caso compartido entre canales. El ejecutivo de sucursal ve la misma ruta que la persona armó en la web.

## Alcance del MVP (demo del viernes)
1. **Jubilación + PGU** de punta a punta: a partir de un RUN del [[datos-dataset-A]], evaluar la PGU con reglas en código y armar la ruta según el resultado (`elegible`, `no_elegible`, `antecedente_faltante`, `proximo`, `ya_recibe`).
2. **Caso "a tiempo"**: detectar a quienes cumplen 65 pronto (17 en el dataset) y avisarles antes, con lo que deben tener listo.
3. Dos canales en la demo: chat web de la persona + vista del ejecutivo sobre el mismo caso.
4. Métricas sobre los 500 perfiles del dataset + usuarios simulados.
5. Nacimiento y cesantía solo como extensión, para mostrar escalabilidad.

## Beneficios candidatos por evento (verificar contra fichas ChileAtiende)
| Evento | Candidatos |
|---|---|
| Nacimiento | Inscripción en Registro Civil, Chile Crece Contigo, asignación familiar, Subsidio Familiar (SUF), permiso postnatal, sala cuna |
| Cesantía | Seguro de Cesantía (AFC), Fondo de Cesantía Solidario, Bolsa Nacional de Empleo, subsidios municipales |
| Jubilación | Solicitud de pensión, Pensión Garantizada Universal (PGU), Bono por hijo |

Los plazos y requisitos exactos salen del catálogo oficial. No se deben inventar: si un dato no está en la fuente, el agente lo dice.

## Datos
- **Dataset A entregado** (jubilación + PGU, 500 perfiles sintéticos): ver [[datos-dataset-A]]. Está en `data/raw/dataset_A_participantes/`.
- Parámetros de la PGU (montos y umbrales): desde la ficha oficial de ChileAtiende, en `data/catalogo/`, con `fuente_url`.
- [ ] Preguntar a los mentores si habrá más datasets (B, ...).

## Enfoque de IA
- **Agente con herramientas** sobre Bedrock (Claude Sonnet 5): entiende el relato, pregunta lo que falta y llama a herramientas deterministas.
- Herramientas: `consultar_perfil` (lee el perfil del dataset por RUN), `evaluar_pgu` / `evaluar_elegibilidad` (reglas), `calcular_plazos` (fechas), `buscar_beneficios` (catálogo), `guardar_caso` / `leer_caso`.
- **Regla clave**: la elegibilidad y los plazos los calcula código, no el LLM. El LLM conversa, explica y cita la fuente.
- **Memoria de caso** compartida entre canales (DynamoDB).
- **Usuarios simulados** con Claude Haiku 4.5: N personas sintéticas por evento conversan con el agente y se mide cuántas terminan con su ruta completa y sin plazos vencidos.

## Servicios AWS
Bedrock (Converse + tool use), Bedrock Knowledge Bases o índice simple sobre S3, DynamoDB, Lambda + API Gateway, EventBridge Scheduler (alertas de plazo), S3. Opcional: Amazon Connect/Lex para el canal telefónico.

## Métricas para el pitch
- PGU no cobradas detectadas en el dataset (preliminar: 37 de 56 personas de 65 o más sin PGU).
- Personas avisadas antes de cumplir 65 (17 en el dataset).
- Antecedentes faltantes detectados, con su ruta para resolverlos.
- % de usuarios simulados que obtienen su ruta completa.
- Beneficios identificados por caso vs. los que la persona conocía al inicio.
- Plazos detectados que habrían vencido sin alerta.
- Tiempo de atención en sucursal cuando el ejecutivo ya recibe el caso armado.

## Encaje con los criterios de evaluación
- **Innovación técnica (25%)**: agente con herramientas + memoria entre canales + evaluación con usuarios simulados.
- **Impacto social (25%)**: beneficios no cobrados y plazos vencidos afectan sobre todo a quienes tienen menos información.
- **Factibilidad (20%)**: servicios serverless gestionados, catálogo oficial como fuente; desplegable por ChileAtiende con los créditos AWS.
- **Escalabilidad (15%)**: añadir un evento de vida = añadir reglas y fichas, no reentrenar.
- **Presentación (15%)**: demo en vivo de una persona por jubilarse, de la web a la sucursal.

## Riesgos
- El dataset no trae los parámetros de la PGU → cargarlos a mano desde la ficha oficial y citarla.
- Alucinación de requisitos o plazos → reglas en código, citas obligatorias, respuesta "no lo sé" permitida.
- Credenciales STS temporales que expiran durante el desarrollo → renovar perfil `hackaton`.
- Alcance: tres eventos y varios canales en 1,5 jornadas. Priorizar jubilación + PGU.

## Preguntas para los mentores
- ~~¿Qué datos entregan y en qué formato?~~ Dataset A (jubilación + PGU). ¿Habrá más datasets? ¿Cómo se evalúa su uso?
- ¿Qué canales usa hoy ChileAtiende y dónde se pierde la continuidad?
- ¿Hay acceso a Amazon Connect en la cuenta del evento?
- ¿Kiro suma puntos?

## Relacionado
[[_seleccion]] · [[arquitectura-chileatiende]] · [[0002-seleccion-reto]] · [[0003-orquestacion-agente]] · [[0004-mvp-jubilacion-pgu]] · [[datos-dataset-A]] · [[board]]
