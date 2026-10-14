---
tipo: rol
integrante: Jonmor
entorno: Kiro IDE Pro
frente: API, casos e invitaciones
---
# Jonmor — API, casos e invitaciones

**Entorno:** Kiro IDE Pro · **Color en el pipeline:** 🟧 Naranjo · Plan general, reglas y mapa del pipeline en [[_equipo]].

## Tareas
- [ ] **T15** · P0 · B1 · Repositorio de casos: interfaz + implementación en memoria — ✅ tests de crear, leer y agregar mensaje · depende de T02
- [ ] **T16** · P0 · B2 · API FastAPI: `POST /cases`, `POST /cases/{id}/messages`, `GET /cases/{id}`, con agente falso inyectable — ✅ test de integración con el agente falso
- [ ] **T17** · P0 · B2 · `GET /personas/{run}/pgu`: evaluación directa sin LLM para el panel del ejecutivo — ✅ devuelve `ResultadoPGU` e hitos · depende de T03, T11 y T12
- [ ] **T18** · P1 · B2 · Repositorio DynamoDB (tabla `cases`) con la misma interfaz — ✅ tests con moto o DynamoDB Local; se elige por variable de entorno
- [ ] **T19** · P0 · B3 · Continuidad entre canales y checklist: cada mensaje guarda su `canal` (web, sucursal); `GET /cases/{id}` devuelve la línea de tiempo y el checklist, y `PATCH /cases/{id}/checklist` lo actualiza — ✅ un caso iniciado en web se ve completo desde la sucursal, sin repetir la historia
- [ ] **T20** · P1 · B3 · `GET /alertas`: personas con un hito próximo a quienes invitar y candidatas preliminares a PGU no cobrada — ✅ usa T12 y T13; test con fecha de referencia fija
- [ ] **T21** · P0 · B2 · Invitación y autorización: `POST /invitaciones` (detectados por T13), `POST /cases/{id}/respuesta` (acepta o declina) y `POST /cases/{id}/autorizacion` (fuentes y finalidad). Sin autorización no se llama a `consultar_perfil` — ✅ test: si la persona declina, el flujo se detiene y queda registrado

## Notas
-
