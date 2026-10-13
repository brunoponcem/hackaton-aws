# Prompts reutilizables

## Arrancar sesión (Claude Code o Codex)
> Lee AGENTS.md, 30-tareas/board.md y la última nota de 40-bitacora/. Toma la primera tarea con tu nombre como dueño, márcala "en curso" y trabaja en una rama propia.

## Arquitecto (Claude Code)
> Con el reto elegido en 10-retos/, propón una arquitectura en 20-arquitectura/ adaptando arquitectura-base.md. Registra las decisiones como ADR. Luego divide el trabajo en tareas para board.md, cada una con dueño y criterio de aceptación.

## Implementador (Codex)
> Implementa la tarea X de board.md. Escribe tests. No toques archivos fuera de lo que la tarea indica. Al terminar, resume cambios en la bitácora del día.

## Revisor (Claude Code)
> Revisa la rama codex/<tarea> contra los criterios de board.md y las convenciones de AGENTS.md. Deja comentarios concretos.

## Cierre del día
> Resume en 40-bitacora/<fecha>.md qué se hizo, qué quedó bloqueado y qué sigue mañana.
