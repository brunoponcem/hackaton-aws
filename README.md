# Hackatón AWS 2026

Repo + vault de Obsidian + espacio de trabajo para Claude Code y Codex.

## Puesta en marcha (una vez)
1. Desde el repo clonado, ejecuta `uv sync` (Python 3.12).
2. Si no tienes `.env`, copia `.env.example`: `Copy-Item .env.example .env` en PowerShell, o `cp .env.example .env` en Bash. Completa perfil, región y modelo; conserva cualquier `.env` existente.
3. Ejecuta `uv run pytest`, `uv run ruff check .` y `uv run ruff format --check .`.
4. Obsidian → *Open folder as vault* → esta carpeta.
5. Abre dos terminales en la raíz: una con `claude`, otra con `codex`.

La base Python y el cliente Bedrock están documentados en [[T01-scaffold-python]]. Las pruebas corren sin credenciales ni llamadas a AWS. El agente conversacional y las vistas se implementan en las tareas siguientes.

## Flujo diario
- Tú decides en Obsidian (retos, arquitectura, tablero).
- Claude Code diseña y revisa; Codex implementa tareas acotadas.
- Cada agente en su rama o worktree: `git worktree add ../hk-codex -b codex/tarea`.
- Todo lo importante queda en `40-bitacora/`.

Reglas para agentes: ver [[AGENTS]].
