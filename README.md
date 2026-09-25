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
  "security": {
    "classification": "security-sensitive",
    "surfaces": ["authentication/session/token"],
    "trust_boundaries": ["refresh token -> session renewal"],
    "abuse_cases": ["replay revoked refresh token"],
    "controls": ["rotation", "revocation", "authorization boundary", "sensitive-token logging protection"],
    "evidence": [],
    "head_sha": null,
    "limitations": [],
    "candidate_disposition": null
  },
  "uncertainties": []
}
```
<!-- gpt-web-vibe:task:end -->
```

Duplicate/mismatched manifest markers are invalid. Schema v1 tasks must be rebuilt into v2 from current GitHub state before normal continuation.

### Optional frontend state

Frontend work uses the same manifest v2 and the same workflow. Only UI tasks add an optional `frontend` block:

```json
{
  "frontend": {
    "surface": "application",
    "intent": "refine",
    "design_context": {
      "path": null,
      "mode": "infer-existing-ui"
    },
    "acceptance_dimensions": [
      "visual-consistency",
      "responsive-behavior",
      "accessibility"
    ],
    "acceptance_map": {
      "visual-consistency": ["AC1"],
      "responsive-behavior": ["AC2"],
      "accessibility": ["AC3"]
    },
    "visual_qa": {
      "max_rounds": 2,
      "browser_tooling": [],
      "evidence": [],
      "head_sha": null,
      "limitations": []
    }
  }
}
```

The classifier is deliberately conservative: React/Next/Vue/etc. presence alone is not enough. Request/target evidence must reach the UI. `DESIGN.md` is optional; if absent, the agent infers the incumbent visual system from bounded current UI code. Frontend verification reuses existing project tooling and never installs a browser runtime solely for this policy. Recorded visual evidence is bound to the current PR head; unavailable visual tooling is reported as a limitation.

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

High-confidence identifiers are persisted in `context.symbols`; source code is not cached in the manifest. Runtime retrieval diagnostics record each selected path, score, round and request/symbol reason. `max_search_rounds` and `max_symbol_hints` are enforced by retrieval, while shallow project paths are considered before deep subtrees when the scan budget is bounded.

## Modes

- `feature` — new capability/project work
- `change` — intentional behavior/compatibility change
- `bug_fix` — defect correction
- `refactor` — structural change while preserving behavior
- `hotfix` — urgent minimal production fix
- `test` — test/coverage work without production behavior change by default
- `docs` — documentation/examples/metadata with minimal code context

## Behavioral coding policy

The kit applies a shared behavioral policy throughout planning, implementation, verification, and GitHub review:

- **Think before coding:** surface material assumptions and tradeoffs. Ask when ambiguity can change behavior, contracts, data, security, compatibility, destructive effects, or scope; minor reversible ambiguity may proceed with an explicit conservative assumption.
- **Simplicity first:** implement the minimum code needed for accepted behavior. Avoid speculative features, single-use abstractions, and unrequested configurability. Defensive branches should correspond to plausible states under established contracts, not invented impossible scenarios.
- **Surgical changes:** avoid unrelated refactors, renames, formatting, cleanup, or deletion. Cleanup is limited to artifacts made obsolete by the current patch.
- **Goal-driven execution:** map non-trivial steps to observable verification evidence. Bugs prefer reproduce -> root cause -> regression -> minimal fix -> verify; refactors establish behavior before and after.
- **Changed-line traceability:** every changed line must trace to the request, an acceptance criterion, required regression/compatibility/security evidence, or cleanup caused by the change.

These rules bias the workflow toward small, reviewable diffs without forcing unnecessary clarification for low-risk reversible decisions.

## Comment and documentation policy

The kit prefers self-explanatory code and uses comments to preserve information the code cannot express clearly. Comment **why**, constraints, invariants, non-obvious tradeoffs, security assumptions, performance/cache reasoning, tricky edge cases and deliberate workarounds. Avoid narration of obvious code and boilerplate docstrings for simple private helpers. Public/shared contracts should be documented when callers need behavior, errors, side effects, lifecycle or invariants. Touched stale comments/docstrings/docs must be updated or removed, and TODO/FIXME notes must be actionable.

## Security policy

The kit does **not** guarantee that generated or modified code is secure. Its auditable rule is:

> **Security-sensitive changes cannot silently pass without explicit security review/evidence.**

```text
PLAN
  ↓
identify security-sensitive surface
  ↓
BUILD
  ↓
secure coding rules
  ↓
VERIFY
  ├─ security diff review
  ├─ project-native security scanner when available
  ├─ dependency vulnerability check when relevant/available
  └─ targeted security tests
  ↓
GITHUB REVIEW
  └─ current-head security evidence required
```

Authentication, authorization, sessions/tokens/passwords, upload/filesystem, user-controlled database queries or URLs, HTML/template rendering, command execution, payments/webhooks and secrets/credentials automatically make the task security-sensitive when found in the request or final impact/diff.

New task manifests persist a `security` object with classification, surfaces, trust boundaries, abuse cases, controls, structured evidence, evidence head SHA and limitations. Older schema-v2 manifests without `security` remain valid for compatibility; an active security-sensitive task should add the block before verification.

For security-sensitive tasks, normal lint/type/test/build or runtime `PASS_VERIFIED` is insufficient by itself. Security evidence must be explicit and bound to the current PR head. The runtime derives conservative candidates from request/path/symbol evidence; if review keeps such a task `standard`, `security.candidate_disposition` must explain why. Missing scanners are reported as limitations rather than silently treated as success.

## Completion gate

`PASS_VERIFIED` requires every acceptance criterion to be `met` with structured evidence. `ready` and `complete` require a current pass. The config-aware completion gate additionally enforces `verification.require_commands`, security-candidate disposition, frontend acceptance mappings, and current-head frontend/security evidence. A new head clears every saved verification outcome and moves a previously ready/complete task back to verification.

```bash
python runtime/vibe_web.py completion-status task.json --config .vibe/config.json
```

Config v2 is a strict contract with its own JSON Schema. CI validates task/project/config templates with Draft 2020-12 JSON Schema as well as the runtime validators.

## Bootstrap

Local:

```bash
python install.py --target /path/to/project
python install.py --target /path/to/project --dry-run
```

The installer preserves an existing `AGENTS.md`, writes the `.vibe` contract and performs lightweight stack detection from common manifests/files. Verification detection respects npm/pnpm/yarn/bun metadata and lockfiles, and it no longer assumes pytest merely because a Python `tests/` directory exists. It can detect common Python/FastAPI/Django/Flask, JS/TS/Next/React/Vue/Nuxt/Svelte/Vite/Nest/Express, Ruby/Rails, PHP/WordPress/Laravel, Go/Rust/Java projects and established verification commands.

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
python runtime/vibe_web.py completion-status task.json --config .vibe/config.json
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
