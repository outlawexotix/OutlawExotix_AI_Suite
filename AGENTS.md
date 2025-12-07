# Repository Guidelines

## Project Structure & Module Organization
- `tools/` holds the core Python utilities: `war_room.py` (main console), `gemini_bridge.py` (Gemini uplink), `codex_bridge.py` (OpenAI/Codex uplink), and `log_memory.py` (shared memory writer).
- `templates/` contains agent personas; copy them into `~/.claude/templates` for runtime use.
- `bin/` provides launchers (`agent.ps1`, `agent.sh`) that stitch a persona together with `memory_protocol.md` before invoking Claude.
- Root docs (`README.md`, `memory_protocol.md`, `CLAUDE.md`) describe usage patterns and shared-memory rules; keep them aligned with code changes.

## Build, Test, and Development Commands
- Install deps: `pip install google-generativeai colorama` (plus `openai` if you use `codex_bridge.py`).
- Run the War Room console: `python tools/war_room.py`.
- Direct Gemini query: `python tools/gemini_bridge.py "Assess this directory"` (add `--api-key` or rely on `GOOGLE_API_KEY`/`.env`).
- Codex/OpenAI query: `python tools/codex_bridge.py "Refactor war_room input loop"` (uses `OPENAI_API_KEY` or `.env`).
- Agent launcher (Windows): `pwsh ./bin/agent.ps1 -Name overwatch -p "Scan this repo"`.

## Coding Style & Naming Conventions
- Python: 4-space indent, prefer type hints for new functions, keep functions small and command-oriented. Favor explicit paths over globals.
- Scripts: mirror platform styles (`.ps1` for Windows, `.sh` for POSIX); keep parameters and env lookups consistent with existing scripts.
- Naming: snake_case for Python, kebab-case for templates, descriptive but short CLI flags.

## Testing Guidelines
- No automated test suite yet; smoke-test changes by running the relevant CLI entry points above.
- When modifying API bridges, verify error paths by omitting keys and by using `--api-key` flag.
- If adding tests, colocate quick checks under `tools/` with clear invocation comments and keep them dependency-light.

## Commit & Pull Request Guidelines
- Use imperative, present-tense commit subjects (e.g., `add gemini key fallback`, `harden war_room prompt`). Keep body lines ≤72 chars.
- Describe what changed and why; mention affected entry points (`war_room`, `gemini_bridge`, `bin/agent.ps1`).
- PRs: include reproduction steps or commands run, note config or key requirements, and attach before/after snippets for user-facing output.

## Security & Configuration Tips
- Do not commit secrets; `.env`, `GOOGLE_API_KEY`, and `OPENAI_API_KEY` should stay local. Prefer `--api-key` flags for ad-hoc runs.
- Treat `CLAUDE_EXE` and other absolute paths in scripts as configurable; expose flags instead of hardcoding new paths.
- Log only what is necessary to `PROJECT_MEMORY.md`; avoid dumping tokens or keys into shared memory.
