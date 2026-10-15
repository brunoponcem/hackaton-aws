---
inclusion: manual
tipo: contexto-tecnico
integrante: Johann
fecha: 2026-10-14
---
# Johann — Contexto técnico completo y acotado

Guía de entrada para **Johann con Kiro de AWS**. Dos personas desarrollan el código: Clemente (Codex + Claude) y Johann (Kiro). **Johann está trabajando desde `src/app`**, según el usuario; no hay reparto por tareas ni carpetas exclusivas. Ambos envían aportes y los integran por merge, incluso si se superponen. No heredar responsabilidades de los cinco roles históricos. Las reglas de dominio de `AGENTS.md` siguen vigentes; esta nota resume el producto y evita recorrer todo el vault.

## Producto y pipeline actual

**ChileAtiende a Tiempo** llega a quien no llega y acompaña jubilación + PGU hasta la derivación a un ejecutivo. Tiene cuatro partes: asistente ciudadano inspirado en ChileAtiende, contacto escalonado, campañas territoriales por heatmap y ficha de back-office para ejecutivos/trabajadores sociales.

Flujo: **detectar → contactar → invitar → autorizar → consultar perfil → evaluar → preparar ruta → recopilar documentos → derivar → seguir/cerrar**. Un único caso conserva contexto entre canales. El asistente orienta; IPS/AFP y el organismo correspondiente deciden. Una evaluación `elegible` nunca concede PGU.

Contacto: **email → llamada → lugar de trabajo → puerta a puerta**. Solo escalar ante falta de respuesta; declinar detiene todo, aceptar lleva a autorización/asistente. Una escalera activa por persona, con todos los intentos registrados. La demo usa reloj simulado. Mensajes laborales no revelan beneficios, montos ni situación de la persona.

El heatmap propone comunas para campañas según casos sin respuesta en última etapa. Diseño todavía propuesto: ranking por número/prioridad y ocultar grupos de menos de 5 personas. No mostrar nombres/direcciones en el mapa. Esperas de 7 días o 3 intentos en 5 días son parámetros de demo propuestos, no normas oficiales. Envíos reales y uso de identidad institucional siguen por confirmar.

## Qué existe y qué falta (aporte integrado, `ed989ad`)

| Pieza | Estado y ubicación |
|---|---|
| Base Python | `pyproject.toml`, `uv.lock`; Python 3.12, uv, ruff, pytest, boto3, pydantic, python-dotenv |
| Contratos compartidos | `src/contracts/{profile,evaluation,case}.py`, exportados en `src/contracts/__init__.py` |
| Consulta de perfil | `src/tools/profiles.py`; RUN con/sin puntos, DV, permisos y separación entre casos |
| Agente conversacional | `src/agent/{bedrock,loop,tools,route,cli,prompts}.py`; Bedrock Converse, tool use, manejo de errores y máximo de iteraciones |
| App de Johann | `src/app/app.py`, Streamlit: persona, ejecutivo, invitaciones simuladas y métricas; `ui_persona.py` implementa la guía ciudadana |
| Portal y ayuda | `src/app/portal.py`: estructura del portal oficial, Inicio/Ayuda/Mi ruta, búsqueda y links oficiales. `ruta/chatbot.py` conecta el chat Bedrock al Agent/cliente común con la ruta autorizada; plantilla sin configuración |
| Motor y casos de la app | `src/app/ruta/`: reglas, hitos, rutas con dependencias, casos SQLite y asistente por plantillas/Bedrock opcional. Autónomo: aún no usa los contratos/agente comunes |
| Embudo de contacto | `ruta/colador.py` y `contacto.py`: backend SQLite, reloj y respuestas simuladas; CLI `scripts/colador_backend.py`; `ui_embudo.py` en campañas y `demo_embudo.py` independiente (8502). No hay envíos reales |
| Reglas y catálogo | `src/rules/` y `data/catalogo/` todavía no existen en el estado revisado |
| API, persistencia y contactos | Por implementar; FastAPI y repositorio en memoria primero, DynamoDB después |
| Frontend y back-office | Por implementar: chat, ficha de beneficiario y campañas/heatmap; framework pendiente |
| Simulación e infraestructura | Por implementar: `src/sim/`, `infra/`; despliegue AWS opcional después de demo local |

La app ya usa el agente común en su chatbot configurado, pero las reglas/SQLite siguen propios. Falta reconciliar estados (`futuro`/`excluido`), historial y persistencia. El embudo funciona en simulación; heatmap y alertas siguen pendientes. `20-arquitectura/backend-embudo-contacto.md` documenta reloj/políticas; `portal-ayuda-tramites.md` la pestaña; `revision-aporte-johann.md` la revisión previa.

## Interfaces de integración

Usar los modelos existentes; identificadores en inglés y valores de estados en español. Si el aporte de `src/app` trae modelos o servicios equivalentes, reconciliarlos durante la integración para conservar una sola implementación y ajustar sus consumidores; no borrar uno únicamente por tener un nombre parecido.

```python
from datetime import date
from src.contracts import Profile, PguResult, Milestone, Case

# Exportar estas funciones desde src/rules/__init__.py cuando se implementen:
def evaluar_pgu(profile: Profile, fecha_ref: date) -> PguResult: ...
def calcular_hitos(profile: Profile, fecha_ref: date) -> list[Milestone]: ...
```

`src/agent/tools.py:build_registry()` las detecta desde `src.rules`; también permite inyectar reglas falsas en tests. No cambiar el agente para incorporar reglas si se respetan estas firmas. Contexto de servidor: `ToolContext(case, reference_date)`; los argumentos del LLM no aportan caso, autorización, perfil ni fecha de evaluación.

- `Profile.model_validate(raw)` carga el JSON con alias españoles; acceder mediante atributos ingleses: `civil_registry.birth_date/sex/life_status`, `rsh.pfp_available/pfp_percentile`, `residence.years_since_age_20/years_last_5`, `pension_fund.estimated_self_funded_pension`, `pensions_benefits`.
- `PguResult`: `run`, `status`, `reference_date`, `reasons`, `preliminary=True`. Estados: `elegible`, `no_elegible`, `antecedente_faltante`, `proximo`, `ya_recibe`. Definir/testear precedencia de motivos en las reglas.
- `Reason`: requisito, `met` (True/False/None), mensaje y `Source`. `Source`: título, URL opcional, fecha de consulta y `verified`. Sin verificación no afirmar cumplimiento normativo definitivo.
- `Milestone`: tipo, fecha, descripción, `is_deadline=False`, fuente. Apertura de solicitud es hito, no vencimiento.
- `Case`: RUN, invitación, autorización, evaluación, hitos, ruta, checklist y mensajes con canal. `can_read_profile` requiere permiso y aceptación si hay invitación.
- `consultar_perfil(run, case=case)` devuelve `Profile`/`None`; sin permiso o con RUN ajeno lanza `PermissionError`. La aplicación entrega el caso de confianza.
- `Agent.run_turn(case, text, channel=...)` devuelve respuesta y actualiza el caso. Envelope de herramientas: `{"ok": true, "data": ...}` o `{"ok": false, "error": {"type", "message"}}`.

API **prevista**, aún no implementada: `POST /cases`, `POST /cases/{id}/messages`, `GET /cases/{id}`. Agregar flujo de aceptación/autorización, contactos, documentos y derivación al diseñar los contratos nuevos. Chat y back-office consumen el mismo caso; no crear historiales separados.

## Datos y reglas de negocio

`data/raw/dataset_A_participantes/perfiles.json`: 500 personas sintéticas, referencia **2026-10-08**, unión por RUN. Para reglas/batch cargar perfiles directamente con pydantic; eso es evaluación offline sintética, no consulta de una persona en el producto. En el flujo ciudadano usar la herramienta autorizada.

Sin RSH/residencia/PFP puede haber antecedente faltante. Sin AFP o información laboral no bloquear automáticamente. Sin pensiones/beneficios significa ninguno según el README. Revisar tipo y `estado=vigente`, no solo existencia de PGU. PFP y PAFE son simulaciones; validar definición oficial de pensión base antes de calcularla.

Faltan parámetros PGU y fuentes oficiales con vigencia/URL/fecha de consulta. Las edades/ventanas del PPT necesitan verificación antes de codificar. Los 37 candidatos y 17 próximos a cumplir 65 son conteos preliminares, no objetivos que deban forzarse en tests.

El dataset **no tiene email, teléfono, empleador, dirección ni comuna**. Pedir dataset adicional o generar capa separada en `data/synthetic/`, con semilla fija y rótulo sintético. No modificar `data/raw/` ni presentar contactos ficticios como reales. No hay motivo para cargar las 64.000 líneas del JSON al chat: inspeccionar un perfil, el README o un test.

## Arranque, pruebas y entrega

Desde la raíz: `uv sync --group app`, `uv run --group app pytest` (64 tests tras portal/chatbot), `uv run --group app python src/app/verificar.py` (500 perfiles, offline). App: `uv run --group app streamlit run src/app/app.py --server.address localhost`. Tests cubren contratos, agentes, navegación y flujo aceptar/autorizar/revocar sin AWS. Ruff histórico de la app sigue pendiente. No instalar requirements autónomo sobre la venv compartida.

Para una prueba real: copiar `.env.example` a `.env` **solo si no existe**, configurar credenciales AWS propias autorizadas y ejecutar `uv run agente --run 100000010-4 --mensaje "¿Qué hago ahora?"`. La CLI simula consentimiento para demo y consume Bedrock; no es el flujo real de autorización. No hace falta AWS para escribir/probar reglas.

Perfil previsto `hackaton`, región `us-east-1`. Modelos de aplicación permitidos según cuenta: `us.anthropic.claude-sonnet-5` (principal), `us.anthropic.claude-opus-5`, `us.anthropic.claude-haiku-4-5`; `*-5-5` y Fable bloqueados. El modelo de Kiro como herramienta de desarrollo es independiente del modelo Bedrock de la aplicación. No se requiere instalar Codex/Claude para Johann.

Trabajar sobre el objetivo inmediato, sin IDs de tareas obligatorios ni reserva exclusiva de archivos. Notas/commits en español, código en inglés, sin credenciales. Registrar qué se aportó, qué se integró y qué falta en `board-johann.md`/`bitacora-johann.md`. Leer solo el código/contrato/test necesario; abrir documentación extensa únicamente ante una duda concreta. No importar todos los boards ni expandir todos los enlaces de Obsidian.

## Commit → merge → verificación → push

1. Revisar `git status` y guardar **solo el aporte propio** con `git add -- <archivos>` y `git commit -m "Descripción del aporte"`. No incluir configuración local de Kiro ni cambios ajenos por accidente.
2. `git fetch origin`; integrar `git merge origin/main` en la rama del aporte. Si se trabaja directamente en `main`, el mismo merge integra los cambios del otro desarrollador.
3. Resolver conflictos preservando la intención de ambos. Revisar también lo que Git fusionó sin conflicto: servicios/rutas duplicados, nombres de campos, imports, dependencias, estado compartido y comportamiento de `src/app` frente a `src/agent`/`src/contracts`. No escoger todo «ours»/«theirs» ni eliminar aportes por defecto.
4. Completar el commit de merge cuando corresponda y verificar el resultado combinado: tests Python, lint/formato y los comandos reales de `src/app` una vez disponibles. Un merge limpio no garantiza compatibilidad lógica.
5. Para publicar en `main`, si se trabajó en rama de aporte, integrar esa rama en `main` con el checkout limpio y volver a verificar. Hacer `git push origin main`. Si el push se rechaza porque otro publicó antes, repetir fetch/merge/verificación/push; **no usar force push** para saltarse sus commits.

Los commits guardan aportes; el merge integra versiones. Este flujo es una acción explícita después de cada aporte y antes de publicar, no un automatismo instalado. No modificar un checkout que esté usando el otro agente a la vez: pueden solaparse los commits, pero cada proceso debe tener su checkout estable.

Referencias puntuales si hacen falta: `20-arquitectura/adr/0005-asistente-contacto-escalonado.md` (producto), `20-arquitectura/contacto-y-campanas.md` (diseño), `20-arquitectura/T02-contratos.md` y `T04-agente.md` (interfaces). Son rutas de consulta, no instrucciones para cargarlas juntas.
