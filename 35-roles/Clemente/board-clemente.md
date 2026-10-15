---
tipo: board
integrante: Clemente
entorno: Claude Code + Codex
---
# Board de Clemente

| | |
|---|---|
| **Entorno** | Claude Code + Codex |
| **Integración** | Commit del aporte → fetch/merge de `origin/main` → resolver y verificar → push |
| **Bitácora** | [[bitacora-clemente]] |
| **Equipo y pipeline** | [[_equipo]] · [[_avance]] |

Lista de pendientes propia, sin tareas asignadas. Ordenada según el pipeline de [[_equipo]].

## En curso

## Por hacer
### Validar con los mentores
- [ ] ¿Hay un dataset con email, teléfono, empleador y provincia (¿dataset B?)?
- [ ] Base legal para la alerta en CESFAM y para el contacto a través del trabajo
- [ ] Uso de la marca e identidad visual de ChileAtiende en el portal
- [ ] Hora exacta de entrega y formato de evaluación

### Colador de contacto ([[contacto-y-campanas]])
- Backend del embudo y demo visual implementados; envíos y campañas presenciales reales quedan fuera de la simulación. Ver [[backend-embudo-contacto]].

### Heatmap y alerta de beneficio
- [ ] `src/app/ruta/alertas.py`: nivel de alerta por RUN; "nivel máximo" en la ficha del ejecutivo
- [ ] Vista simulada del punto de atención CESFAM, con mensaje mínimo ("derivar a ChileAtiende")

### Acompañamiento y back-office
- [ ] Checklist de documentos (pendiente, recibido, validado) guiado por el asistente
- [ ] Derivación al ejecutivo con un resumen del caso
- [ ] Ficha del beneficiario: datos con fuente, consentimientos, historial del colador, documentos y estado de las solicitudes

### Unificación y calidad
- [ ] Unificar los dos motores (app de Johann y contratos/agente): estados `futuro` y `excluido`, repositorio e historial ([[revision-aporte-johann]]). Coordinar con Johann
- [ ] Contratos: canales de contacto, `ContactAttempt`, `AlertLevel`, `DocumentItem`, `RequestStatus`
- [ ] Prompt: sin una evaluación disponible, no explicar requisitos de memoria
- [ ] `normalize_run`: aceptar RUN sin guion
- [ ] Lint de `src/app` (190 observaciones pendientes)

### Demo
- [ ] Guion de la demo: embudo del colador → heatmap → persona que llega con alerta → acompañamiento → ejecutivo

## Bloqueos
- Datos reales de contacto/provincia siguen pendientes de los mentores. La capa sintética desbloquea el colador de demo y puede alimentar el futuro heatmap; no representa domicilios reales.

## Hecho
- [x] Área propuesta sobre el heatmap por máxima cobertura espacial, radio ajustable, jornadas por capacidad y descargas JSON/GeoJSON — `66dbea8`, 126 tests · [[heatmap-campanas-simulado]]
- [x] Calor distribuido por persona, direcciones/coordenadas ficticias dentro de su comuna, puntos inspeccionables y compatibilidad con escenarios anteriores — `643a888`, 113 tests · [[heatmap-campanas-simulado]]
- [x] Rediseño RM: calles detalladas, 52 límites comunales BCN, concentración con conteos, escala fija, escenario sintético RM y vista de región completa — `475100e`, 99 tests; Chrome 1440/1024 px a doble densidad · [[heatmap-campanas-simulado]]
- [x] Heatmap de campañas por provincia sintética, ranking con umbral de 5 y propuesta descargable de despliegue según personal/capacidad — `b4d517f`, 90 tests · [[heatmap-campanas-simulado]]
- [x] Capa de contacto sintética rotulada (500 filas) — `7d1d8e0` · [[backend-embudo-contacto]]
- [x] Backend `src/app/ruta/colador.py` y CLI por lotes: reloj, saltos, tres llamadas en cinco días, inicio/rechazo y persistencia — `7d1d8e0`
- [x] Respuestas simuladas con semilla fija y efecto ilustrativo de edad; sin LLM ni envíos — `7d1d8e0`
- [x] Embudo en Detectar e invitar y laboratorio independiente en localhost:8502 — `7d1d8e0`, 84 tests pasan · [[backend-embudo-contacto]]
- [x] Base Python, contratos compartidos, consulta autorizada del perfil, prompt y herramientas, y agente con Bedrock Converse (T01–T05, ver [[bitacora-clemente]])
- [x] Reestructuración de la idea central: [[0005-asistente-contacto-escalonado]] y [[contacto-y-campanas]]
