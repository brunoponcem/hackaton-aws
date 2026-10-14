# ChileAtiende a Tiempo · MVP Jubilación + PGU

Prototipo del desafío IPS/ChileAtiende: detecta hitos, invita, pide autorización, arma una ruta personalizada, acompaña con un asistente y mide el avance. La IA explica; las reglas están en código y AFP/IPS resuelven.

## Ejecutar (desde `src/app/`)
```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements.txt
.\.venv\Scripts\python verificar.py        # chequeos sobre los 500 perfiles
.\.venv\Scripts\streamlit run app.py --server.address localhost
```
Lee `perfiles.json` desde `data/raw/dataset_A_participantes/` en la raíz del repo. Se puede cambiar con la variable `DATA_DIR`.

La app no tiene login: es para demo local. `--server.address localhost` evita exponerla en la red.

IA generativa (opcional): define `BEDROCK_MODEL_ID` (por ejemplo `us.anthropic.claude-sonnet-5`) junto con `AWS_PROFILE=hackaton` y `AWS_REGION=us-east-1`. Sin ella, el asistente responde con plantillas a partir del mismo contexto.

## Vistas
- **Ruta de la persona**: guía ciudadana paso a paso (invitación → autorización → tu situación → tu ruta) con asistente.
- **Vista ejecutivo**: el mismo caso con requisitos, fuentes e historial, para sucursal o call center.
- **Detectar e invitar**: segmentos sobre los 500 perfiles y campaña de invitación simulada.
- **Medición**: KPIs del PPT sobre los casos de la demo.

## Estructura
| Archivo | Rol (paso del PPT) |
|---|---|
| `ruta/config.py` | Parámetros PGU y edades legales, con fuente |
| `ruta/reglas.py` | Hitos, orientación PGU y jubilación, segmento de campaña (Detectar) |
| `ruta/rutas.py` | Pasos con dependencias y fechas (Preparar la ruta) |
| `ruta/casos.py` | SQLite: invitación, autorización, pasos, historial por canal (Acompañar) |
| `ruta/asistente.py` | Mensaje de invitación y explicación; Bedrock o plantillas (Invitar / Acompañar) |
| `ui_persona.py` | Interfaz ciudadana |
| `app.py` | Navegación y vistas ejecutivo, campaña y medición |

## Resultados PGU (precedencia)
`excluido` (fallecido) → `ya_recibe` → `futuro` (>12 meses para los 65) → `no_elegible` → `antecedente_faltante` → `proximo` → `elegible`.
Un incumplimiento verificable pesa más que un antecedente faltante, porque conseguir el antecedente no cambiaría el resultado.

## Pendiente de integrar con el resto del repo
Este MVP es autónomo: todavía no usa `src/contracts/`, `src/tools/` ni `src/agent/`. Los identificadores están en español, a diferencia de la convención del repo (código en inglés).
