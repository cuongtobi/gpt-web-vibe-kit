---
name: bootstrap
description: Initializes the small durable project contract required by gpt-web-vibe-kit in a GitHub repository.
---

# Bootstrap

## Goal
Prepare a target repository for ChatGPT Web continuity without introducing task-specific state on the default branch.

## Procedure
1. Read existing repository instructions and project metadata first.
2. Do not overwrite an existing `AGENTS.md`. If it exists, preserve it and add only compatible project-specific guidance when explicitly authorized.
3. Materialize or update:
   - `.vibe/config.json`
   - `.vibe/project-context.json`
   - `.vibe/README.md`
4. Detect a small stable project summary from current source/manifests:
   - project name/summary;
   - languages and primary language;
   - frameworks;
   - important entrypoints;
   - established test/lint/typecheck/build commands;
   - context limits;
   - dependency authority = advisory/static-best-effort.
5. Keep `.vibe/project-context.json` small. It is a routing summary, not a source-code cache.
6. Do not create `current-task.json`, task folders, or historical chat dumps on the default branch.
7. Verify JSON is valid and that any configured commands actually exist in project configuration.

## Output
Report files created/preserved and any project facts that could not be determined safely.
