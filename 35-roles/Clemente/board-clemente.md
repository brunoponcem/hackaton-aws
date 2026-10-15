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
- 

## Por hacer
### Validar con los mentores
- [ ] ¿Hay un dataset con email, teléfono, empleador y provincia (¿dataset B?)?
- [ ] Base legal para la alerta en CESFAM y para el contacto a través del trabajo
- [ ] Uso de la marca e identidad visual de ChileAtiende en el portal
- [ ] Hora exacta de entrega y formato de evaluación

### Colador de contacto ([[contacto-y-campanas]])
- [ ] Capa de contacto: la de los mentores o una sintética rotulada (`data/synthetic/contacto.csv`, con email, teléfono, empleador y región/provincia/comuna)
- [ ] `src/app/ruta/colador.py`: email a todos → llamada → trabajo → presencial, con reloj simulado, "declinar detiene todo" y tests
- [ ] Respuestas simuladas con semilla fija (iniciar el trámite por etapa, según la edad) y rotuladas como simuladas
- [ ] Embudo por etapa en la vista "Detectar e invitar"

### Heatmap y alerta de beneficio
- [ ] Heatmap por provincia de quienes no respondieron a ninguna etapa, con ranking de campañas y sin mostrar provincias con menos de 5 personas
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
- El colador y el heatmap necesitan datos de contacto y provincia, que no vienen en el dataset A.

## Hecho
- [x] Base Python, contratos compartidos, consulta autorizada del perfil, prompt y herramientas, y agente con Bedrock Converse (T01–T05, ver [[bitacora-clemente]])
- [x] Reestructuración de la idea central: [[0005-asistente-contacto-escalonado]] y [[contacto-y-campanas]]
