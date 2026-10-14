---
tipo: board
integrante: Jp
color: rojo
entorno: Kiro IDE Pro
frente: Infra, simulador, medición y pitch
---
# 🟥 Board de Jp — Infra, simulador, medición y pitch

| | |
|---|---|
| **Entorno** | Kiro IDE Pro |
| **Carpetas de código propias** | `infra/`, `src/sim/`, `60-pitch/` |
| **Ramas** | `jp/T<nn>-<descripcion>` |
| **Commits** | `T<nn>: <qué hiciste>` |
| **Bitácora** | [[bitacora-jp]] |
| **Equipo, mapa y reglas** | [[_equipo]] · [[_avance]] |

Cómo se usa: mueve la línea de la tarea entre secciones. Marca `[x]` solo cuando se cumpla el criterio ✅ y la tarea esté en `main`.

## En curso
- 

## Por hacer
- [ ] **T29** · P0 · B1 · Preguntas a los mentores: ¿dataset B?, ¿cómo se evalúa?, ¿Amazon Connect?, ¿Kiro suma?, hora exacta de entrega, y pedir el estudio de experiencia usuaria 2025 que cita el PPT. Además, `cdk bootstrap` en la cuenta del evento — ✅ respuestas en [[datos-dataset-A]]; bootstrap OK
- [ ] **T30** · P1 · B2 · CDK en `infra/`: DynamoDB `cases`, S3 (dataset + catálogo), Lambda + API Gateway con adaptador Mangum, CORS y permisos de Bedrock solo para los modelos permitidos — ✅ `cdk synth` sin errores y la API corre igual en local y en Lambda
- [ ] **T31** · P1 · B3 · Deploy y URL pública + front apuntando a ella — ✅ demo accesible desde otro computador · depende de T30
- [ ] **T32** · P1 · B2 · Simulador de usuarios en `src/sim/` con Haiku 4.5: cada persona simulada parte de un perfil del dataset, acepta o declina la invitación y conversa con la API — ✅ corre N=20 sin errores
- [ ] **T33** · P0 · B3 · Medición en dos capas. (a) Métricas técnicas del MVP con T13 y el simulador: rutas completas, antecedentes faltantes detectados e invitaciones a tiempo. (b) KPI del piloto del PPT (próximo paso ≥70%, comprensión ≥80%, continuidad ≥90%) con denominadores y evidencia definidos, presentados como metas y no como resultados — ✅ números trazables a un script; lo simulado está separado de lo real
- [ ] **T34** · P0 · B3 · Pitch deck en `60-pitch/`: problema (la historia de Rosa), solución, demo, impacto, arquitectura, escalabilidad y factibilidad, alineado a los criterios (25/25/20/15/15). Las cifras institucionales del PPT se usan solo como contexto, sin restarlas entre sí — ✅ revisado por todo el equipo antes de las 21:00 del jueves
- [ ] **T35** · P0 · B4 · Ensayo del pitch + plan B: video grabado de la demo por si falla en vivo — ✅ video listo antes de las 10:00 del viernes

## Bloqueos
-

## Hecho
-
