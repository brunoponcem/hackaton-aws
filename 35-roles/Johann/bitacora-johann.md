---
tipo: bitacora-integrante
integrante: Johann
---
# Bitácora de Johann

Una entrada por avance o commit relevante, la más reciente arriba. Así se puede seguir el historial de cada tarea sin leer todo `git log`.

Formato: `### AAAA-MM-DD HH:MM · T<nn> · <commit corto>` y debajo qué se hizo, qué falta y si algo bloquea a otro integrante.

### 2026-10-14 · Portal de ayuda y chatbot (Codex)
- `src/app/portal.py` agrega estructura del portal oficial y pestaña de ayuda. `ui_persona` mantiene ruta/permisos; ahora muestra chat desde la invitación.
- El chat configurado delega en `src/app/ruta/chatbot.py` y reutiliza Agent, prompt y BedrockClient compartidos; contexto proviene del motor existente, sin cambiar reglas. SQLite sigue igual.
- 64 tests + verificador OK. Guía [[portal-ayuda-tramites]]. Mantener la navegación y el adaptador al integrar próximos aportes en `src/app`.

### 2026-10-14 · Revisión del aporte `0d06dab` / merge `ed989ad`
- App Streamlit recibida e integrada localmente sin conflictos. Se conservó el motor y las vistas; agregados grupo uv `app`, tests de consentimiento y recorrido UI aceptar/autorizar/preguntar/revocar.
- Corregidos historial tras revocación, consulta Bedrock sin permiso, autorización sin aceptación y verificador que podía usar Bedrock. 61 tests + verificador de 500 perfiles OK.
- [[revision-aporte-johann]] registra duplicaciones/estados incompatibles y simplificación de pensión base; no se da por unificado el agente CLI con la app. Lint completo de `src/app` pendiente.

### 2026-10-14 · Flujo de aportes e integración
- El usuario confirmó que Johann trabaja desde `src/app`; ambos desarrolladores aportarán sin tareas asignadas. El código de esa carpeta aún no aparece en el checkout revisado.
- Actualizadas las guías: commit propio → fetch/merge → resolver conflictos y duplicaciones → verificar → push. Ante avance remoto, repetir; no forzar el push ni descartar el aporte ajeno.
- Se retiró la lista de tareas asignadas del board de Johann. No se instaló un merge automático: la resolución lógica requiere revisar el resultado combinado.

### 2026-10-14 · Contexto exclusivo de Johann · preparación por Codex
- Revisado el producto actual (ADR 0005), contacto escalonado, heatmap, acompañamiento y código del agente/contratos. Clemente y Johann desarrollarán el código; el usuario confirmó que el reparto aún no está definido y Johann debe conocer todo el proyecto.
- Entrada técnica compacta en [[contexto-codear-johann]] y setup local en [[inicio-kiro-johann]]. Board actualizado sin asignar módulos nuevos ni alterar el setup de Clemente.
- Configuración de Kiro bajo demanda, filtro local y `preparar_kiro.py`; no se instaló en el checkout de Clemente. `--check` verifica inclusión manual, tamaño acotado, idempotencia y rechazo de sobrescrituras. Ruff check/format OK.
- Falta instalar/activar en el IDE de Johann y comprobar la reducción efectiva allí. No se afirma que `AGENTS.md` deje de cargarse ni que se haya medido el uso de tokens de Kiro.

