---
name: bootstrap
description: Initializes the durable GitHub-native project contract and detects basic project metadata for ChatGPT Web.
---

# Bootstrap

## Goal
Prepare a repository for ChatGPT Web continuity without creating task-specific state on the default branch.

## Procedure
1. Read existing repository instructions and manifests first.
2. Never overwrite an existing `AGENTS.md`.
3. Create or update:
   - `.vibe/config.json`;
   - `.vibe/project-context.json`;
   - `.vibe/README.md`.
4. Detect a small stable project summary:
   - project name;
   - languages and primary language;
   - frameworks;
   - important entrypoints;
   - established test/lint/typecheck/build commands.
5. Use lightweight repository heuristics only. Prefer root manifests and common framework files; do not build a full source index.
6. Keep `.vibe/project-context.json` small. It is routing metadata, not a source cache.
7. Configure manifest schema v2 and bounded-context limits from `.vibe/config.json`.
8. When creating a new `AGENTS.md`, include the kit's Behavioral Coding Policy, Comment & Documentation Policy, and Security Policy. Never overwrite an existing `AGENTS.md`; the workflow skills still apply these policies even when repository-local instructions are preserved.
9. Verify the generated JSON and only record verification commands that are supported by project configuration.

## Detection hints
- Python: `pyproject.toml`, requirements files, `.py`, FastAPI/Django/Flask imports.
- JS/TS: `package.json`, `tsconfig.json`, framework dependencies/scripts.
- Ruby/Rails: `Gemfile`, `config/routes.rb`, Rails layout.
- WordPress/PHP: `composer.json`, `functions.php`, theme `style.css`, theme/plugin layout.
- Go/Rust/Java: native manifests and conventional entrypoints.

Local `install.py` performs the same basic detection without third-party dependencies.

## Output
Report files created/preserved, detected stack/entrypoints/verification commands, and anything that could not be determined safely.
