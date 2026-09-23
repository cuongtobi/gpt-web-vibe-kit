# gpt-web-vibe-kit

[Tiếng Việt](README_vi.md) · [Detailed usage guide](docs/usage.md) · [PR task contract](docs/pr-task-contract.md)

A GitHub-native vibe-coding kit for **ChatGPT Web + GitHub**, designed for personal small/medium repositories without a persistent local checkout or external context service.

```text
session -> plan -> build -> verify -> github-review
```

## Design goals

- GitHub is durable state; old chat history is optional.
- A new session loads a **bounded** current neighborhood, not the whole repository.
- Task state belongs to the pull request, so concurrent tasks do not overwrite each other.
- Retrieval is lightweight and symbol-aware, using GitHub search in a few bounded rounds.
- Verification is valid only for the exact current PR head SHA.
- No vector database, daemon, LSP server, graph database or external backend is required.

## State model

Stable project state:

```text
AGENTS.md
.vibe/config.json
.vibe/project-context.json
```

Per-task state:

```text
one pull request
├── branch/head SHA
├── one schema-v2 task manifest
├── current diff
├── CI/checks
└── review discussion
```

Live source always comes from the current GitHub branch.

## Manifest v2

Every managed PR contains **exactly one** block:

```text
<!-- gpt-web-vibe:task:start -->
```json
{
  "schema_version": 2,
  "task_id": "jwt-refresh",
  "mode": "bug_fix",
  "status": "building",
  "request": "Fix refresh token after session expiry",
  "base_branch": "main",
  "base_sha": "<base-sha>",
  "head_branch": "vibe/bug_fix/jwt-refresh",
  "head_sha": "<head-sha>",
  "targets": ["app/services/auth.py"],
  "context": {
    "symbols": ["refresh_access_token"],
    "dependencies": ["app/security/token.py"],
    "consumers": ["app/api/auth.py"],
    "tests": ["tests/test_auth.py"],
    "config_files": [],
    "observed_files": [
      {
        "path": "app/services/auth.py",
        "sha": "<github-blob-sha>",
        "role": "target",
        "depth": 0,
        "symbols": ["refresh_access_token"]
      }
    ]
  },
  "acceptance": [
    {
      "id": "AC1",
      "expected": "Expired access can be refreshed with a valid refresh token.",
      "status": "pending",
      "evidence": []
    }
  ],
  "verification": {
    "commands": ["pytest tests/test_auth.py"],
    "head_sha": null,
    "ci_run_id": null,
    "status": null
  },
  "uncertainties": []
}
```
<!-- gpt-web-vibe:task:end -->
```

Duplicate/mismatched manifest markers are invalid. Schema v1 tasks must be rebuilt into v2 from current GitHub state before normal continuation.

## Hard context budget

`.vibe/config.json` contains enforced limits:

```json
{
  "context": {
    "max_dependency_depth": 2,
    "max_source_files": 15,
    "max_test_files": 6,
    "max_related_modules": 6,
    "rebuild_changed_ratio": 0.5,
    "max_search_rounds": 3,
    "max_symbol_hints": 24
  }
}
```

`observed_files.role` and `observed_files.depth` make the saved neighborhood auditable. If a task cannot fit safely, reduce/split scope instead of loading more files.

## New-session restore

```text
AGENTS.md
-> .vibe/config.json
-> .vibe/project-context.json
-> selected PR
-> strict manifest v2
-> current diff
-> current blob SHAs
-> budget check
-> CONTEXT_HIT / CONTEXT_REFRESH / CONTEXT_REBUILD
-> bounded current files
-> current-head CI
```

- `CONTEXT_HIT`: observed references are unchanged and fit the budget.
- `CONTEXT_REFRESH`: a bounded minority changed.
- `CONTEXT_REBUILD`: scope/baseline changed, the manifest is invalid/stale, too much changed, or the saved neighborhood exceeds budget.

## Iterative symbol-aware retrieval

The `plan` skill searches in bounded rounds:

```text
request/error/route keywords
-> promising files
-> relevant symbols
-> symbol/import search
-> direct dependencies/consumers/tests
-> stop at budget
```

High-confidence identifiers are persisted in `context.symbols`; source code is not cached in the manifest.

## Modes

- `feature` — new capability/project work
- `change` — intentional behavior/compatibility change
- `bug_fix` — defect correction
- `refactor` — structural change while preserving behavior
- `hotfix` — urgent minimal production fix
- `test` — test/coverage work without production behavior change by default
- `docs` — documentation/examples/metadata with minimal code context

## Bootstrap

Local:

```bash
python install.py --target /path/to/project
python install.py --target /path/to/project --dry-run
```

The installer preserves an existing `AGENTS.md`, writes the `.vibe` contract and performs lightweight stack detection from common manifests/files. It can detect common Python/FastAPI/Django/Flask, JS/TS/Next/React/Vue/Nuxt/Svelte/Vite/Nest/Express, Ruby/Rails, PHP/WordPress/Laravel, Go/Rust/Java projects and established verification commands.

On ChatGPT Web, use `skills/bootstrap/SKILL.md` to create the same contract directly through GitHub.

## ChatGPT Web usage

New task:

```text
@GitHub work with <owner>/<repo>.
Use cuongtobi/gpt-web-vibe-kit and run the full vibe workflow.

Task:
Fix refresh-token rotation after an expired session.
```

Continue in another session:

```text
@GitHub continue PR #42 in <owner>/<repo>.
Use cuongtobi/gpt-web-vibe-kit.
Restore context from the schema-v2 PR manifest before continuing.
```

Test-only:

```text
@GitHub work with <owner>/<repo>.
Use cuongtobi/gpt-web-vibe-kit.
Add regression tests for <module>. Use mode test and do not change production behavior.
```

Docs-only:

```text
@GitHub work with <owner>/<repo>.
Use cuongtobi/gpt-web-vibe-kit.
Update <docs>. Use mode docs and load code only to verify documentation claims.
```

See [docs/usage.md](docs/usage.md) for complete workflows.

## Verification

Statuses:

- `PASS_VERIFIED`
- `FAIL_VERIFICATION`
- `NEEDS_VERIFICATION_CONFIG`

A pass is valid only when:

```text
verification.head_sha == task.head_sha == current PR head SHA
```

A new commit invalidates older PASS evidence.

## Runtime helpers

```bash
python runtime/vibe_web.py validate-config .vibe/config.json
python runtime/vibe_web.py validate-project .vibe/project-context.json
python runtime/vibe_web.py validate-task task.json --config .vibe/config.json
python runtime/vibe_web.py validate-pr-body pr-body.md --config .vibe/config.json
python runtime/vibe_web.py budget-status task.json --config .vibe/config.json
python runtime/vibe_web.py context-status task.json current-shas.json --config .vibe/config.json
python runtime/vibe_web.py detect-project /path/to/project
```

Runtime code remains Python-standard-library-only.

## Tests

```bash
python -m unittest discover -s tests -v
python -m py_compile install.py runtime/state.py runtime/retrieval.py runtime/vibe_web.py
```

The repository includes three small integration fixtures (FastAPI, Next.js and Rails) covering bootstrap detection and iterative retrieval, plus regression tests for HIT/REFRESH/REBUILD, duplicate manifests, hard budgets and current-head verification.
