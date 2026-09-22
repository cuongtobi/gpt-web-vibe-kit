# ChatGPT Web + GitHub project instructions

This project uses the workflow from `cuongtobi/gpt-web-vibe-kit`.

## Workflow
```text
session -> plan -> build -> verify -> github-review
```

An implementation request authorizes plan/build/verify within the requested scope unless the user explicitly asks for planning only or another approval boundary.

## New-session continuity
Do not depend on previous chat history.

1. Read this file.
2. Read `.vibe/config.json` and `.vibe/project-context.json`.
3. Resolve the active task from the user-specified PR/branch/task or an open vibe PR.
4. Read the task manifest embedded in that PR body.
5. Fetch current GitHub code only for the bounded relevant neighborhood.
6. Read the current PR diff and current-head CI.

Task state belongs to the PR, not to a shared `current-task.json` on `main`.

## Dependency policy
Static dependency discovery is advisory and best-effort. Dynamic imports, DI, generated code/routes, framework registries, macros, reflection and framework runtime wiring require project-native tests/analyzers or direct inspection.

## Verification
Never report `PASS_VERIFIED` without checks that actually ran against the current PR head SHA.
