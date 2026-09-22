---
name: build
description: Implements the planned GitHub change with minimal scope while keeping the PR task manifest usable by later web sessions.
---

# Build

## Goal
Implement the planned behavior with the smallest correct and reviewable diff.

## Before editing
1. Confirm current PR head and task manifest.
2. Re-run session refresh if referenced files changed since planning.
3. Read target files and only the dependency/consumer/test files required for implementation.
4. Preserve unrelated existing changes.

## Rules
- Follow current project patterns and framework conventions.
- Do not add speculative abstractions.
- Do not silently break public APIs, config, schemas, persisted data or wire formats.
- Avoid unrelated formatting/refactors.
- Update focused tests with behavior changes.
- Expand context only when a concrete import, consumer, failing test, contract or runtime relationship requires it.

## bug_fix
Add/identify a regression test that fails for the expected reason before the fix when feasible. Fix the root cause, not the assertion.

## refactor
Keep behavior stable. Update every affected consumer discovered by planning and search again for old symbol/module references after edits.

## After editing
1. Review changed files/diff.
2. Refresh target/dependency/consumer/test references and their blob SHAs.
3. Update PR manifest status to `verifying`.
4. Hand off to `verify`.

Implementation is not verification.
