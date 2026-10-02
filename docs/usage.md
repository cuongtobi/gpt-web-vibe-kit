# Usage

This page is the entry point for using `gpt-web-vibe-kit` on **ChatGPT Web + GitHub**.

```text
session -> plan -> build -> verify -> github-review
```

Choose what you want to do; implementation details live in reference docs rather than here.

## Start here

- New repository or new objective: [Start a new task](workflows/new-task.md)
- Existing PR or another ChatGPT session: [Continue an existing task](workflows/continue-task.md)
- Need a ready-to-paste prompt: [Prompt library](prompts/common.md)

## Choose a workflow

| Goal | Guide | Mode |
| --- | --- | --- |
| Build a new capability or project | [New task](workflows/new-task.md) | `feature` |
| Change existing behavior | [Feature/change](workflows/feature-change.md) | `change` |
| Fix a defect | [Bug fix](workflows/bug-fix.md) | `bug_fix` |
| Preserve behavior while changing structure | [Refactor](workflows/refactor.md) | `refactor` |
| Add regression/coverage tests only | [Test-only](workflows/test-only.md) | `test` |
| Update README/docs/examples/metadata | [Docs-only](workflows/docs-only.md) | `docs` |
| Change UI/frontend behavior or presentation | [Frontend](workflows/frontend.md) | task-dependent |

Urgent minimal production fixes use `hotfix` and follow the bug-fix discipline with the smallest safe scope.

## Task operations

These are task-lifecycle operations, not separate modes:

- [CI failure](operations/ci-failure.md)
- [Review an existing PR](operations/review.md)
- [Rebase or base-branch change](operations/rebase.md)
- [Merge](operations/merge.md)
- [Concurrent tasks](operations/concurrent-tasks.md)

## Reference

Use these only when you need to understand the contract:

- [Task manifest](reference/task-manifest.md)
- [Context and restore](reference/context.md)
- [Verification and completion](reference/verification.md)
- [Security](reference/security.md)
- [Configuration](reference/configuration.md)

## Prompt library

- [English prompts](prompts/common.md)
- [Vietnamese prompts](prompts/common-vi.md)

## Source of truth

Human-facing usage belongs in `docs/`. Agent behavior belongs in `skills/`. Machine contracts belong in `schemas/` and `runtime/`. Repository-local instructions belong in `AGENTS.md`.

This separation avoids duplicating long policy text across usage pages.
