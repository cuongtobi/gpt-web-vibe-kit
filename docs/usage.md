# Using gpt-web-vibe-kit

This guide explains how to use `gpt-web-vibe-kit` on **ChatGPT Web + GitHub** for common software-development tasks.

Standard workflow:

```text
session -> plan -> build -> verify -> github-review
```

The kit does not depend on old chat history. Durable state comes from the GitHub repository, task branch, pull request task manifest, current source, diff and current-head CI.

## 1. Bootstrap an existing repository

```text
@GitHub work with <owner>/<repo>.

Use cuongtobi/gpt-web-vibe-kit.
Read skills/bootstrap/SKILL.md and bootstrap this repository.

Preserve an existing AGENTS.md.
Detect the stack, frameworks, entrypoints and established test/lint/typecheck/build commands.
```

Bootstrap creates the small durable project contract under `.vibe/`.

## 2. Build a new project

```text
@GitHub work with <owner>/<repo>.
Use cuongtobi/gpt-web-vibe-kit.

Build a new <project description>.

Requirements:
- ...
- ...
- ...

Run the full vibe workflow.
```

Flow:

```text
requirements
-> project bootstrap
-> architecture plan
-> task branch + PR
-> implementation
-> tests/config/docs
-> CI
-> verify
```

For greenfield work, initial context comes from requirements, stack decisions, manifests and generated structure. Once code exists, the task PR stores bounded target/test/dependency references for future sessions.

## 3. Add a feature

```text
@GitHub work with <owner>/<repo>.
Use cuongtobi/gpt-web-vibe-kit.

Add <feature>.

Requirements:
- preserve <existing contract>;
- add focused tests;
- avoid new dependencies unless necessary.

Run the full vibe workflow.
```

Flow:

```text
feature request
-> target discovery
-> dependencies
-> consumers/contracts
-> tests
-> plan
-> build
-> verify
```

Search by routes, components, classes, functions, stable strings/error text and import usage, not filenames alone.

## 4. Change existing behavior

Use mode `change`.

The plan should explicitly separate:

```text
current behavior
-> desired behavior
-> compatibility contract
-> affected consumers
-> tests
```

Pay special attention to public APIs, configuration, persisted schemas, serialized data and backward compatibility.

## 5. Fix a bug

```text
@GitHub work with <owner>/<repo>.
Use cuongtobi/gpt-web-vibe-kit.

Fix:
<symptom>.

Reproduce the bug first.
Find the root cause.
Add a regression test.
Apply the smallest root-cause fix.
Run affected checks and full current-head verification.
```

Required flow:

```text
REPRODUCE
-> ROOT CAUSE
-> FAILING REGRESSION TEST
-> MINIMAL FIX
-> PASSING REGRESSION TEST
-> AFFECTED TESTS
-> VERIFY
```

Context normally expands from symptom/query -> matching symbol/file -> target -> dependencies -> consumers -> related tests.

Do not fix based on an unproven guess.

## 6. Production hotfix

Use mode `hotfix`.

Keep the patch minimal:
- no opportunistic cleanup;
- no unrelated rename;
- no dependency upgrade unless required by the fault;
- no unrelated refactor;
- add regression coverage when feasible.

## 7. Write tests for existing code

```text
@GitHub work with <owner>/<repo>.
Use gpt-web-vibe-kit.

Add tests for <module>.

Cover:
- happy path;
- invalid input;
- important errors;
- regression-prone edge cases.

Do not change production behavior unless explicitly requested.
```

If new tests expose a real bug outside scope, report it instead of silently changing production behavior.

## 8. Increase coverage

Prioritize business-critical behavior, error paths, security boundaries and regression-prone code. Do not write tests whose only value is increasing a percentage.

## 9. Refactor a function/class/module

```text
@GitHub work with <owner>/<repo>.
Use gpt-web-vibe-kit.

Refactor <target>.
Preserve behavior and public contracts.

Before editing:
- find dependencies and all discoverable direct consumers;
- capture baseline behavior/tests;
- record invariants.

After editing:
- search for old references;
- run affected tests and current-head CI.
```

Flow:

```text
target
-> dependencies
-> all discoverable consumers
-> tests/contracts
-> baseline
-> refactor
-> old-reference search
-> verify unchanged behavior
```

## 10. Large refactor

When a refactor spans many modules, first map public boundaries and consumer impact. Split the migration into reviewable PRs when one PR would be too broad.

Typical sequence:

```text
PR1: introduce boundary
PR2: migrate consumers
PR3: remove old implementation
```

## 11. Rename a symbol/module/API

Treat it as `refactor`.

Search:
- imports/usages;
- string references;
- DI/registry/config references;
- serialization/public docs when relevant;
- tests.

## 12. Add an API endpoint

Typical bounded context:

```text
route/controller
-> request/response schema
-> service/use-case
-> repository/data boundary
-> auth/middleware
-> tests
```

## 13. Database/schema migration

Inspect model, migration, serializers/DTOs, API contracts, queries, existing-data compatibility and tests. Define a safe strategy for old rows/data.

## 14. Add a package

Before adding a package:
- check whether the repo already has equivalent capability;
- justify the new dependency;
- verify compatibility;
- update lockfiles;
- add suitable verification.

## 15. Upgrade a dependency/framework

Use mode `change`.

Analyze relevant breaking changes, build an impact map, split migration steps when necessary, and run the broad affected test/build set.

## 16. Frontend feature

Typical bounded context:

```text
route/page
-> feature UI
-> hook/composable/store
-> API/data layer
-> tests
```

For Next.js, Nuxt and SvelteKit, inspect server/client boundaries and framework-native routing.

## 17. Frontend bug

Do not assume the visible component is the root cause. Check query cache, stores, mutation handling, stale props and server/client data boundaries.

## 18. WordPress plugin/theme

Do not modify WordPress core. Inspect hooks/filters, REST routes, options/meta, template/block contracts, enqueue behavior and compatibility. Static hook wiring remains best-effort.

## 19. Rails/Laravel/Django/Nest and framework magic

Do not rely only on static imports. Inspect framework registration, DI, routes, callbacks, autoloading and project-native tooling/tests.

## 20. Plan only

```text
@GitHub work with <owner>/<repo>.
Use gpt-web-vibe-kit.

PLAN ONLY. Do not edit code.

Analyze:
<task>
```

Workflow stops after `session -> plan`.

## 21. Review a PR

```text
@GitHub review PR #42 in <owner>/<repo>.
Use gpt-web-vibe-kit/skills/github-review/SKILL.md.

Check:
- task-manifest scope;
- bugs/regressions;
- missing consumers;
- compatibility;
- tests;
- unresolved review threads;
- current-head CI.
```

A new PR head makes previous review evidence stale for changed code.

## 22. Verify only

```text
@GitHub work with PR #42 in <owner>/<repo>.
Use gpt-web-vibe-kit.

Run only verify + github-review.
Compare acceptance criteria against the final diff and current-head CI.
```

Possible status:
- `PASS_VERIFIED`
- `FAIL_VERIFICATION`
- `NEEDS_VERIFICATION_CONFIG`

## 23. Continue in a new ChatGPT session

```text
@GitHub continue PR #42 in <owner>/<repo>.
Use cuongtobi/gpt-web-vibe-kit.

Restore context from the PR task manifest before continuing.
```

Flow:

```text
project context
-> PR manifest
-> current head
-> compare observed blob SHAs
-> CONTEXT_HIT / CONTEXT_REFRESH / CONTEXT_REBUILD
-> fetch bounded current code
-> continue
```

No old chat transcript is required.

## 24. Continue when the PR number is unknown

Ask ChatGPT to find the open vibe PR matching task title, branch, request or task_id. If several candidates remain, list them instead of guessing.

## 25. Code changed between sessions

Stored blob SHAs are compared with the current branch:

- `CONTEXT_HIT`: relevant references unchanged.
- `CONTEXT_REFRESH`: refresh a bounded changed subset and its neighborhood.
- `CONTEXT_REBUILD`: scope/baseline changed materially or too much of the observed context changed.

## 26. Branch was rebased

Re-evaluate context and impact before continuing. If rebase materially changes target/dependency relationships, rebuild bounded context.

## 27. CI failure

Inspect failed job -> failed step -> logs -> root cause. Make a scoped fix, then verify the new head. Old CI becomes stale immediately after the head changes.

## 28. Repository has no meaningful checks

Return `NEEDS_VERIFICATION_CONFIG`. Add stack-appropriate tests, lint, typecheck, build or smoke verification instead of using a no-op command.

## 29. Merge

The kit does not merge by default.

```text
@GitHub check PR #42.
If the current head is PASS_VERIFIED and there are no blockers,
squash merge it into main.
```

## 30. Concurrent tasks

Use one branch + PR per task. Task state is isolated in each PR body; feature, bug-fix and refactor work can proceed independently.

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
reproduce -> root cause -> regression test -> minimal fix -> affected checks -> verify.
```

## Refactor

```text
@GitHub work with <owner>/<repo>.
Use cuongtobi/gpt-web-vibe-kit.

Refactor:
<target>

Preserve behavior/public contracts.
Find dependencies and direct consumers.
Capture baseline before editing.
Search old references after editing.
Verify the current head.
```

## Test-only

```text
@GitHub work with <owner>/<repo>.
Use cuongtobi/gpt-web-vibe-kit.

Add tests for:
<module/feature>

Cover:
<cases>

Do not change production behavior unless requested.
```

## Continue

```text
@GitHub continue PR #<number> in <owner>/<repo>.
Use cuongtobi/gpt-web-vibe-kit.
Restore context from the PR manifest and continue.
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
Compare acceptance criteria with the current-head diff and CI.
```

# Mode selection

| Work | Mode |
| --- | --- |
| New project/feature | `feature` |
| Existing behavior/compatibility change | `change` |
| Defect correction | `bug_fix` |
| Structural change with preserved behavior | `refactor` |
| Urgent minimal production fix | `hotfix` |
| Test-only work | test-only task; normally no production behavior change |

# Core operating rules

1. One real task should normally use one PR.
2. Continue sessions from the PR, not pasted chat history.
3. Persist references, not source copies.
4. Current GitHub code outranks historical manifest data.
5. Static dependency evidence is advisory.
6. Bugs require root-cause evidence before fixes.
7. Refactors require consumer discovery and baseline behavior.
8. Verification must belong to the current head SHA.
9. A new head makes old CI/review evidence stale.
10. Missing meaningful checks means `NEEDS_VERIFICATION_CONFIG`, never a fake pass.
