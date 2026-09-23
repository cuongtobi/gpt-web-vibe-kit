---
name: build
description: Implements the planned GitHub change with minimal scope while keeping the v2 PR task manifest current.
---

# Build

## Goal
Implement the planned behavior with the smallest correct and reviewable diff.

## Before editing
1. Confirm current PR head and schema-v2 task manifest.
2. Re-run session refresh if referenced files changed.
3. Confirm current context remains within the hard budget.
4. Read only the target/dependency/consumer/test files required for implementation.
5. Preserve unrelated changes.

## Rules
- Follow existing project patterns.
- Avoid speculative abstractions and unrelated cleanup.
- Do not silently break APIs/config/schemas/persisted data/wire formats.
- Update focused tests with behavior changes.
- Expand context only for concrete evidence and never beyond configured hard limits.
- When scope cannot fit safely, split the task/PR instead of bypassing the budget.

## `test` mode
Prefer test-only changes. Production behavior changes require explicit task scope.

## `docs` mode
Change docs/examples/metadata and only the minimum source/config needed to keep documentation accurate.

## After editing
1. Review the diff.
2. Refresh paths, symbols, roles, depths and blob SHAs.
3. Update manifest `head_sha`.
4. A changed head invalidates older `PASS_VERIFIED` evidence.
5. Set task status to `verifying`.
6. Hand off to `verify`.

Implementation is not verification.
