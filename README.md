# Hackatón AWS 2026

Repo + vault de Obsidian + espacio de trabajo para Claude Code y Codex.

## Puesta en marcha (una vez)
1. `git init && git add . && git commit -m "estructura inicial"`
2. Obsidian → *Open folder as vault* → esta carpeta.
3. `./scripts/check-env.sh` e instala lo que falte.
4. `cp .env.example .env` y completa tu perfil AWS.
5. Abre dos terminales en la raíz: una con `claude`, otra con `codex`.

## Flujo diario
- Tú decides en Obsidian (retos, arquitectura, tablero).
- Claude Code diseña y revisa; Codex implementa tareas acotadas.
- Cada agente en su rama o worktree: `git worktree add ../hk-codex -b codex/tarea`.
- Todo lo importante queda en `40-bitacora/`.

Reglas para agentes: ver [[AGENTS]].
