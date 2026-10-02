# gpt-web-vibe-kit

[Tiếng Việt](README_vi.md) · [Usage](docs/usage.md) · [Prompt library](docs/prompts/common.md) · [Task reference](docs/reference/task-manifest.md)

A GitHub-native coding workflow for **ChatGPT Web + GitHub**, optimized for personal small/medium repositories.

```text
session -> plan -> build -> verify -> github-review
```

The central idea is simple: **GitHub is durable state; old chat history is optional.**

## Quick start

### 1. Bootstrap a repository

```text
@GitHub work with <owner>/<repo>.

Use cuongtobi/gpt-web-vibe-kit.
Read skills/bootstrap/SKILL.md and bootstrap this repository.

Preserve any existing AGENTS.md.
Detect the stack, entrypoints and established verification commands.
```

### 2. Start a task

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

### 3. Continue in another ChatGPT session

```text
@GitHub continue PR #<number> in <owner>/<repo>.
Use cuongtobi/gpt-web-vibe-kit.
Restore context from the schema-v2 PR manifest before continuing.
```

No old chat transcript is required.

## Choose a workflow

- [Start a new task](docs/workflows/new-task.md)
- [Continue an existing task](docs/workflows/continue-task.md)
- [Fix a bug](docs/workflows/bug-fix.md)
- [Add or change a feature](docs/workflows/feature-change.md)
- [Refactor safely](docs/workflows/refactor.md)
- [Test-only work](docs/workflows/test-only.md)
- [Docs-only work](docs/workflows/docs-only.md)
- [Frontend/UI work](docs/workflows/frontend.md)

For CI failure, review, rebase, merge and concurrent work, see [task operations](docs/usage.md#task-operations).

## How it works

Each managed task uses one branch and one pull request. The PR body stores exactly one schema-v2 task manifest containing bounded references to targets, symbols, dependencies, consumers, tests, acceptance criteria and current-head verification evidence.

The workflow keeps source live on GitHub instead of copying code into persistent task state. Context is bounded by `.vibe/config.json`, and verification becomes stale when the PR head changes.

## Optional frontend state

UI tasks may add the optional `frontend` manifest block for preserve-vs-redesign intent, acceptance mapping and bounded visual-QA evidence. Non-UI tasks omit it.

See [Frontend workflow](docs/workflows/frontend.md).

## Security

Security-sensitive work stays in the same workflow but cannot silently pass without explicit current-head security evidence. The kit does not claim that generated code is security-guaranteed.

See [Security reference](docs/reference/security.md).

## Documentation map

- [Usage router](docs/usage.md) — choose what you want to do.
- [Prompt library](docs/prompts/common.md) — copy/paste prompts.
- [Task manifest](docs/reference/task-manifest.md) — durable PR task state.
- [Context](docs/reference/context.md) — bounded retrieval and restore.
- [Verification](docs/reference/verification.md) — current-head evidence and completion.
- [Security](docs/reference/security.md) — classification and evidence.
- [Configuration](docs/reference/configuration.md) — `.vibe/config.json`.

## Repository development checks

These commands are for developing this kit itself:

```bash
python -m pip install "jsonschema>=4,<5"
python -m unittest discover -s tests -v
python -m py_compile install.py runtime/state.py runtime/retrieval.py runtime/vibe_web.py
```

Runtime code remains Python-standard-library-only.
