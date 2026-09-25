# Using gpt-web-vibe-kit

This guide covers the normal coding workflows for `gpt-web-vibe-kit` on **ChatGPT Web + GitHub**.

The kit is intentionally optimized for personal small/medium repositories. It does not require a local daemon, vector database, persistent checkout, LSP server or external context backend.

Standard workflow:

```text
session -> plan -> build -> verify -> github-review
```

Durable state comes from the repository and the task PR, not old chat history.

---

## 1. First-time repository bootstrap

Prompt:

```text
@GitHub work with <owner>/<repo>.

Use cuongtobi/gpt-web-vibe-kit.
Read skills/bootstrap/SKILL.md and bootstrap this repository.

Preserve any existing AGENTS.md.
Detect the stack, frameworks, entrypoints and established verification commands.
```

Bootstrap creates or updates:

```text
AGENTS.md
.vibe/config.json
.vibe/project-context.json
.vibe/README.md
```

The project context is intentionally small. It records routing facts, not source code.

### Local bootstrap

```bash
python install.py --target /path/to/project
python install.py --target /path/to/project --dry-run
```

The local installer performs lightweight detection from common manifests/files.

---

## 2. What a new session reads

A normal session restores state in this order:

```text
AGENTS.md
-> .vibe/config.json
-> .vibe/project-context.json
-> selected PR
-> exactly one schema-v2 task manifest
-> current diff
-> observed blob SHA comparison
-> hard-budget check
-> CONTEXT_HIT / CONTEXT_REFRESH / CONTEXT_REBUILD
-> bounded current files
-> current-head CI/reviews
```

Do not paste an old chat transcript as the primary continuation mechanism.

---

## 3. Hard context budget

The values in `.vibe/config.json` are hard limits, not suggestions.

Default v2 limits:

```json
{
  "max_dependency_depth": 2,
  "max_source_files": 15,
  "max_test_files": 6,
  "max_related_modules": 6,
  "rebuild_changed_ratio": 0.5,
  "max_search_rounds": 3,
  "max_symbol_hints": 24
}
```

If a task cannot fit safely:

1. reduce scope;
2. split the task/PR;
3. avoid loading unrelated code.

Do not bypass the budget to make a task appear complete.

---

## 4. Iterative symbol-aware retrieval

Planning uses GitHub search in bounded rounds.

### Round 1: direct evidence

Search exact or strong evidence:

- error/trace text;
- route/endpoint names;
- config keys;
- user-provided identifiers;
- task keywords.

### Round 2: symbols

Read only promising files, then identify relevant:

- functions;
- classes;
- types/interfaces;
- constants;
- modules/import specifiers.

Persist high-confidence identifiers in `context.symbols`, then search them.

### Round 3: direct neighborhood

Search direct:

- dependencies/imports/requires;
- consumers/usages;
- tests;
- config/schema/API/framework registration.

Stop as soon as the target and required neighborhood are clear.

An empty search result does not prove there is no impact.

---

## 5. Create a new project

```text
@GitHub work with <owner>/<repo>.
Use cuongtobi/gpt-web-vibe-kit.

Build a new <project description>.

Requirements:
- ...
- ...

Run the full vibe workflow.
```

Typical flow:

```text
requirements
-> bootstrap project contract
-> architecture/stack decisions
-> branch + PR + schema-v2 manifest
-> implementation
-> tests/config/docs
-> current-head verification
-> review
```

Mode: `feature`.

---

## 6. Add a feature

```text
@GitHub work with <owner>/<repo>.
Use cuongtobi/gpt-web-vibe-kit.

Add <feature>.

Requirements:
- preserve <contract>;
- add focused tests;
- avoid new dependencies unless necessary.

Run the full workflow.
```

Typical bounded context:

```text
request
-> exact target
-> public/data/config contracts
-> direct dependencies
-> direct consumers
-> tests
```

Mode: `feature`.

---

## 7. Change existing behavior

Use mode `change`.

Plan:

```text
current behavior
-> desired behavior
-> compatibility requirements
-> affected consumers/contracts
-> tests
```

Pay special attention to APIs, configuration, persisted schemas, serialized data and backward compatibility.

---

## 8. Fix a bug

```text
@GitHub work with <owner>/<repo>.
Use cuongtobi/gpt-web-vibe-kit.

Fix:
<symptom>.

Required:
reproduce/locate -> root cause -> regression test -> minimal fix -> affected checks -> verify.
```

Flow:

```text
symptom/error
-> candidate files
-> relevant symbols
-> target/root cause
-> regression test
-> minimal fix
-> affected tests
-> current-head verification
```

Mode: `bug_fix`.

Do not fix a guessed root cause without evidence.

---

## 9. Production hotfix

Use mode `hotfix`.

Rules:

- smallest safe patch;
- no opportunistic cleanup;
- no unrelated rename/refactor;
- no dependency upgrade unless required;
- regression coverage when feasible;
- current-head verification before completion.

---

## 10. Test-only work

Use mode `test`.

```text
@GitHub work with <owner>/<repo>.
Use cuongtobi/gpt-web-vibe-kit.

Add tests for <module/behavior>.

Cover:
- happy path;
- invalid input;
- important errors;
- regression-prone edge cases.

Use mode test.
Do not change production behavior unless explicitly requested.
```

Context should focus on:

```text
production target
-> current behavior/contract
-> existing test harness/helpers
-> relevant edge cases
```

If tests expose an out-of-scope production bug, report it rather than silently fixing it.

---

## 11. Coverage improvement

Still use mode `test`.

Prioritize:

1. business-critical behavior;
2. security/error boundaries;
3. regressions;
4. complex branching.

Do not write low-value tests only to raise a percentage.

---

## 12. Documentation-only work

Use mode `docs`.

```text
@GitHub work with <owner>/<repo>.
Use cuongtobi/gpt-web-vibe-kit.

Update:
<README/docs/API guide>.

Use mode docs.
Read source/config only where needed to verify documentation claims.
Do not expand into unrelated code refactors.
```

Typical context:

```text
documentation target
-> source/config that proves claims
-> examples/links
-> documentation checks/CI
```

This mode avoids unnecessary dependency expansion.

---

## 13. Refactor a function/class/module

```text
@GitHub work with <owner>/<repo>.
Use cuongtobi/gpt-web-vibe-kit.

Refactor <target>.
Preserve behavior and public contracts.

Before editing:
- find direct dependencies;
- find all reasonably discoverable direct consumers;
- capture baseline tests/behavior;
- record invariants.

After editing:
- search old references;
- run affected checks;
- verify current head.
```

Mode: `refactor`.

Flow:

```text
target symbol
-> direct dependencies
-> direct consumers
-> tests/contracts
-> baseline
-> refactor
-> old-reference search
-> verify unchanged behavior
```

---

## 14. Large refactor

Do not bypass context limits. Split work when needed.

Example:

```text
PR1: introduce new boundary
PR2: migrate consumers
PR3: remove old implementation
```

Each PR gets its own schema-v2 manifest and verification evidence.

---

## 15. Rename symbol/module/API

Treat as `refactor`.

Search:

- symbol usages;
- imports/requires;
- strings/config/registry references;
- framework wiring;
- public docs;
- tests.

After editing, search the old symbol/path again.

---

## 16. Add an API endpoint

Typical context:

```text
route/controller
-> request/response schema
-> service/use-case
-> repository/data boundary
-> auth/middleware
-> tests
```

Persist route/service/schema symbols when they are useful continuation anchors.

---

## 17. Database/schema migration

Inspect only the relevant bounded neighborhood:

- model/schema;
- migration;
- serializer/DTO/API contract;
- affected queries;
- existing-data compatibility;
- tests.

Acceptance criteria should include behavior for existing data where relevant.

---

## 18. Add a package

Before adding a dependency:

- check whether existing code already solves the need;
- justify the new package;
- verify version compatibility;
- update lockfiles;
- run relevant tests/build;
- document meaningful new configuration.

Mode is usually `feature` or `change`.

---

## 19. Upgrade a dependency/framework

Use mode `change`.

Analyze breaking changes relevant to this repository, not the entire upstream changelog. Build a bounded impact map and run broad enough affected checks.

---

## 20. Frontend feature

Frontend work stays in the same workflow; there is no separate design/polish/audit command. Classify it from concrete request/target evidence, not from framework presence alone.

Typical bounded context:

```text
route/page
-> component
-> theme/tokens/styles
-> hook/composable/store
-> API/data layer
-> tests
```

When applicable, persist the optional manifest `frontend` block. Use `intent: refine` for local UI improvement that preserves the current visual language; use `redesign` only when the request authorizes a visual-language change.

`DESIGN.md` is optional. Read it when present and relevant; otherwise infer the incumbent design system from bounded current tokens/theme/shared components/styles/nearby screens. Do not create it merely because it is absent.

Select only materially relevant acceptance dimensions from:

```text
visual-consistency
responsive-behavior
interaction-states
accessibility
content-layout-integrity
```

Visual QA reuses existing browser/E2E/story/screenshot tooling only and is bounded to one inspection round plus at most one confirmation round. If visual tooling is unavailable, record the limitation and do not claim visual behavior was verified.

For Next.js/Nuxt/SvelteKit, inspect server/client boundaries and file-system routing.

---

## 21. Frontend bug

Do not assume the visible component is the root cause. Search state/cache/data-flow symbols and direct consumers before editing.

Common areas:

- query cache invalidation;
- stores;
- mutation handling;
- stale props;
- server/client boundaries.

---

## 22. WordPress theme/plugin

Do not modify WordPress core.

Inspect:

- hooks/filters;
- REST registration;
- shortcodes/blocks;
- options/meta;
- templates;
- enqueue behavior.

Dynamic hook composition is advisory/static-best-effort; verify with project-native checks/manual integration where necessary.

---

## 23. Rails/Laravel/Django/Nest and framework magic

Static imports are not enough. Use framework adapter hints and inspect routes, DI/providers, callbacks, autoloading/registries and native tests.

---

## 24. Plan only

```text
@GitHub work with <owner>/<repo>.
Use cuongtobi/gpt-web-vibe-kit.

PLAN ONLY. Do not edit code.

Task:
<description>
```

Run:

```text
session -> plan
```

The PR manifest may remain in `planning`.

---

## Behavioral coding policy

Apply these rules throughout the task:

- state material assumptions/tradeoffs before implementation;
- ask only when ambiguity can materially change behavior, contracts, data, security, compatibility, destructive effects, or scope;
- for minor/reversible ambiguity, state a conservative assumption and continue;
- prefer the simplest implementation that satisfies the acceptance criteria;
- avoid speculative features, single-use abstractions and unrequested configurability;
- keep the diff surgical: no unrelated refactor, rename, reformat or cleanup;
- add defensive handling only for plausible states under established contracts;
- require every changed line to trace to the request, acceptance evidence, required regression/compatibility/security work, or cleanup caused by the patch;
- express non-trivial plan steps as **step -> verification evidence** and retry only when new evidence or a concrete change justifies it.

## Comment and documentation policy

During build/review:
- prefer self-explanatory names/structure;
- comment **why**, invariants, constraints and non-obvious tradeoffs rather than obvious what;
- document public/shared contracts when useful;
- keep TODO/FIXME actionable;
- update/remove stale comments/docstrings/docs in touched areas;
- reject comment noise added only to increase density.

## Security-sensitive work

The kit does not promise "secure code". It guarantees a workflow requirement instead: security-sensitive changes cannot silently pass without explicit security review/evidence.

Automatically classify a task as security-sensitive when request/impact/diff touches auth/authz, sessions/tokens/passwords, upload/filesystem, user-controlled DB queries or URLs, HTML/template rendering, command execution, payments/webhooks, secrets/credentials or another comparable trust boundary.

Example — refresh token:

```text
rotation / expiry
revocation
replay risk
cookie flags
session fixation
authorization boundary
secret/token logging
```

Example — file upload:

```text
file size
extension/MIME
path traversal
filename sanitization
overwrite behavior
execution risk
storage boundary
authorization
```

For these tasks, persist `security` state in the v2 manifest and require current-head security diff review + targeted tests/checks + scanner/dependency-audit evidence when available/relevant. Runtime also derives conservative candidates from request/path/symbol evidence. If review keeps a candidate task `standard`, record a non-empty `security.candidate_disposition`. Missing tooling is an explicit limitation, not a silent pass.

## 25. Verify only

```text
@GitHub work with PR #<number> in <owner>/<repo>.
Use cuongtobi/gpt-web-vibe-kit.

Run only verify + github-review.
Compare acceptance criteria with the final diff and current-head CI.
```

Statuses:

- `PASS_VERIFIED`
- `FAIL_VERIFICATION`
- `NEEDS_VERIFICATION_CONFIG`

A PASS requires every acceptance criterion to be `met` with structured evidence. Before `ready`/`complete`, run the config-aware completion gate:

```bash
python runtime/vibe_web.py completion-status task.json --config .vibe/config.json
```

This additionally checks required verification commands, security-candidate disposition, frontend `acceptance_map`, and current frontend/security evidence.

---

## 26. Review an existing PR

```text
@GitHub review PR #42 in <owner>/<repo>.
Use gpt-web-vibe-kit/skills/github-review/SKILL.md.

Check:
- exactly one valid schema-v2 manifest;
- manifest head matches PR head;
- context fits hard budget;
- scope/compatibility;
- missing consumers;
- tests;
- unresolved review threads;
- current-head CI.
```

---

## 27. Continue in a new ChatGPT session

```text
@GitHub continue PR #42 in <owner>/<repo>.
Use cuongtobi/gpt-web-vibe-kit.
Restore context from the schema-v2 task manifest before continuing.
```

No old chat transcript is required.

---

## 28. PR number is unknown

Ask ChatGPT to find the open vibe PR matching:

- task ID;
- branch;
- title;
- request.

If multiple candidates remain, list them instead of guessing.

---

## 29. `CONTEXT_HIT`

Use when the unique v2 manifest is valid, budget-compliant and observed blob SHAs are unchanged.

Fetch only the current files needed for the immediate next step.

---

## 30. `CONTEXT_REFRESH`

Use when a bounded minority of observed files changed.

Refresh changed files and only their directly necessary relationships, then update blob SHAs/symbols/depths.

---

## 31. `CONTEXT_REBUILD`

Use when:

- manifest is missing/duplicated/invalid/v1;
- task scope materially changed;
- base/rebase invalidated the prior neighborhood;
- too many observed files changed;
- context exceeds hard limits;
- old targets are no longer relevant.

A rebuild remains bounded. It does not mean loading the whole repository.

---

## 32. Rebase or base branch changed

Re-evaluate target/dependency/consumer relationships. If the baseline changed materially, use `CONTEXT_REBUILD`.

---

## 33. CI failure

Flow:

```text
failed run
-> failed job
-> failed step/log
-> root cause
-> scoped fix
-> new head
-> all saved verification outcomes/head/run stale and cleared
-> ready/complete returns to verifying
-> verify new head
```

Do not rerun blindly when the failure is deterministic and actionable.

---

## 34. Repository has no meaningful checks

Use:

```text
NEEDS_VERIFICATION_CONFIG
```

Do not add a no-op command to manufacture a pass. Establish a stack-appropriate test/lint/typecheck/build/smoke check when task scope permits.

---

## 35. Verification head binding

Manifest stores:

```json
{
  "head_sha": "abc123",
  "verification": {
    "head_sha": "abc123",
    "ci_run_id": 123456,
    "status": "PASS_VERIFIED"
  }
}
```

PASS is valid only when both SHAs also match the actual current PR head.

Any new commit makes old pass evidence stale.

---

## 36. Acceptance evidence

Each criterion uses structured evidence:

```json
{
  "id": "AC1",
  "expected": "Refresh succeeds after access expiry.",
  "status": "met",
  "evidence": [
    {
      "type": "test",
      "ref": "tests/test_auth.py::test_refresh_after_expiry"
    },
    {
      "type": "ci",
      "ref": "run:123456"
    }
  ]
}
```

Do not mark a criterion met based on unsupported prose.

---

## 37. Schema-v1 PR migration

Schema v1 is not normal continuation state in v2.

For an old active PR:

1. read current base/head/diff;
2. rebuild the bounded neighborhood;
3. add `context.symbols`;
4. add observed `role`, `depth`, `symbols`;
5. convert acceptance evidence to structured lists;
6. add `verification.head_sha`;
7. replace the old block with exactly one v2 block;
8. verify against current head before claiming PASS.

---

## 38. Concurrent tasks

Use one branch + PR per real task:

```text
PR #41 feature
PR #42 bug fix
PR #43 docs
```

There is no shared `current-task.json`.

---

## 39. Merge

The kit does not merge by default.

```text
@GitHub check PR #42.
If the current head is PASS_VERIFIED and there are no blockers,
squash merge it into main.
```

Merge only with explicit authorization or repository instructions that clearly authorize it.

---

# Recommended prompt templates

## Full implementation

```text
@GitHub work with <owner>/<repo>.

Use cuongtobi/gpt-web-vibe-kit and run the full vibe workflow.

Task:
<description>

Requirements:
- ...
- ...

Respect the repository hard context budget.
Do not expand scope.
Only consider the task complete with current-head verification.
```

## Bug fix

```text
@GitHub work with <owner>/<repo>.
Use cuongtobi/gpt-web-vibe-kit.

Fix:
<symptom>

Required:
reproduce/locate -> root cause -> regression test -> minimal fix -> affected checks -> verify.
Use iterative symbol-aware search and keep context bounded.
```

## Refactor

```text
@GitHub work with <owner>/<repo>.
Use cuongtobi/gpt-web-vibe-kit.

Refactor:
<target>

Preserve behavior/public contracts.
Find direct dependencies and consumers.
Capture baseline.
Search old references after editing.
Verify current head.
```

## Test-only

```text
@GitHub work with <owner>/<repo>.
Use cuongtobi/gpt-web-vibe-kit.

Mode: test

Add tests for:
<module/feature>

Cover:
<cases>

Do not change production behavior unless requested.
```

## Docs-only

```text
@GitHub work with <owner>/<repo>.
Use cuongtobi/gpt-web-vibe-kit.

Mode: docs

Update:
<README/docs>

Use only the code/config context needed to verify documentation claims.
```

## Continue

```text
@GitHub continue PR #<number> in <owner>/<repo>.
Use cuongtobi/gpt-web-vibe-kit.
Restore the strict v2 manifest, check budget/blob SHAs, then continue.
```

## Plan only

```text
@GitHub work with <owner>/<repo>.
Use cuongtobi/gpt-web-vibe-kit.

PLAN ONLY. Do not edit code.

Task:
<description>
```

## Verify only

```text
@GitHub work with PR #<number> in <owner>/<repo>.
Use cuongtobi/gpt-web-vibe-kit.

Run only verify + github-review.
Require verification.head_sha to match the current PR head.
```

---

# Mode selection

| Work | Mode |
| --- | --- |
| New project/feature | `feature` |
| Existing behavior/compatibility change | `change` |
| Defect correction | `bug_fix` |
| Structural change preserving behavior | `refactor` |
| Urgent minimal production fix | `hotfix` |
| Test/coverage-only work | `test` |
| README/docs/examples/metadata | `docs` |

---

# Core rules

1. One real task normally uses one PR.
2. Continue from GitHub state, not pasted chat history.
3. Require exactly one strict schema-v2 manifest block.
4. Persist references/symbols/blob SHAs, never source copies.
5. Respect hard context limits.
6. Use iterative symbol-aware retrieval instead of filename-only search.
7. Static dependency evidence is advisory.
8. Bugs require evidence-supported root cause.
9. Refactors require consumer discovery and baseline behavior.
10. `PASS_VERIFIED` must belong to the current head SHA.
11. New commits invalidate old PASS evidence.
12. Missing meaningful checks means `NEEDS_VERIFICATION_CONFIG`, not a fake pass.
13. Comments document non-obvious rationale; do not narrate obvious code, and keep touched documentation current.
14. Security-sensitive changes require explicit current-head security evidence; never treat normal PASS as a security guarantee.
