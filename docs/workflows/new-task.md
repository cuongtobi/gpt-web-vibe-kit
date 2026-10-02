# Start a new task

Use this when starting a new objective in a repository. If the repository has not been bootstrapped yet, bootstrap it first with `skills/bootstrap/SKILL.md`.

## Flow

```text
session -> classify mode -> branch/PR -> plan -> build -> verify -> github-review
```

Planning should find the smallest safe target/dependency/consumer/test neighborhood and keep it inside the configured context budget.

## Prompt

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

Use `feature` for new capability/project work and `change` when intentionally changing existing behavior or compatibility.

## Done means

- requested behavior is implemented with bounded scope;
- acceptance criteria have evidence;
- verification belongs to the current PR head;
- frontend/security evidence is present when the task requires it;
- PR review has no unresolved blocker.
