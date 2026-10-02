# Prompt library

Copy the smallest template that matches the task.

## Bootstrap a repository

```text
@GitHub work with <owner>/<repo>.

Use cuongtobi/gpt-web-vibe-kit.
Read skills/bootstrap/SKILL.md and bootstrap this repository.

Preserve any existing AGENTS.md.
Detect the stack, frameworks, entrypoints and established verification commands.
```

## Full implementation

```text
@GitHub work with <owner>/<repo>.
Use cuongtobi/gpt-web-vibe-kit and run the full vibe workflow.

Task:
<description>

Requirements:
- preserve <contract>;
- add focused tests;
- avoid new dependencies unless necessary.
```

## Bug fix

```text
@GitHub work with <owner>/<repo>.
Use cuongtobi/gpt-web-vibe-kit.

Fix:
<symptom>

Required:
reproduce/locate -> root cause -> regression test -> minimal fix -> affected checks -> verify.
```

## Refactor

```text
@GitHub work with <owner>/<repo>.
Use cuongtobi/gpt-web-vibe-kit.

Refactor <target>.
Preserve behavior/public contracts.
Find direct dependencies and consumers, capture baseline, search old references after editing, and verify the current head.
```

## Test only

```text
@GitHub work with <owner>/<repo>.
Use cuongtobi/gpt-web-vibe-kit.

Mode: test
Add tests for <module/behavior>.
Do not change production behavior unless explicitly requested.
```

## Docs only

```text
@GitHub work with <owner>/<repo>.
Use cuongtobi/gpt-web-vibe-kit.

Mode: docs
Update <README/docs/examples>.
Use only source/config needed to verify documentation claims.
```

## Continue

```text
@GitHub continue PR #<number> in <owner>/<repo>.
Use cuongtobi/gpt-web-vibe-kit.
Restore the schema-v2 manifest and current GitHub state before continuing.
```

## Review

```text
@GitHub review PR #<number> in <owner>/<repo>.
Use cuongtobi/gpt-web-vibe-kit.
Check scope, current-head verification, acceptance evidence and unresolved blockers.
```

## Merge

```text
@GitHub check PR #<number>.
If the current head is ready with no blockers, squash merge it into main.
```
