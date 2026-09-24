---
name: session
description: Restores bounded project and task context from GitHub at the start of a ChatGPT Web session.
---

# Session

## Goal
Reconstruct enough current context to continue safely without loading the whole repository or depending on previous chat history.

## Bootstrap order
1. Read target `AGENTS.md`.
2. Read `.vibe/config.json` and `.vibe/project-context.json`.
3. Resolve the task:
   - explicit PR/branch/task first;
   - otherwise the uniquely matching open vibe PR;
   - list candidates instead of guessing when ambiguous.
4. Read the selected PR metadata/body.
5. Require exactly one manifest block and `schema_version: 2`. Restore manifest `security` classification/surfaces/evidence when present; older v2 manifests without it remain readable for compatibility.
6. Read the current PR changed filenames/diff.
7. Fetch current blob SHAs for every observed file from the PR head.
8. Apply the hard budget from `.vibe/config.json` before expanding context.
9. Treat security evidence as stale when `security.head_sha` does not match the current PR head. Do not carry old security evidence forward as current proof.

A duplicate/mismatched manifest block is invalid. A v1 task must be rebuilt into v2 from current GitHub state before normal continuation.

## Hard budget
The configured values are limits, not suggestions:
- `max_dependency_depth`;
- `max_source_files`;
- `max_test_files`;
- `max_related_modules`;
- `rebuild_changed_ratio`.

Each `observed_files` entry records `role`, `depth`, `symbols` and blob `sha`, allowing budget/depth checks to be deterministic. If the saved neighborhood exceeds the configured hard budget, choose `CONTEXT_REBUILD` and reduce/split scope instead of loading more.

## Context decision

### CONTEXT_HIT
Use when scope is unchanged, observed SHAs are current and the manifest fits the hard budget.

### CONTEXT_REFRESH
Use when only a bounded minority changed. Refresh those files plus direct dependency/consumer/test relationships needed for the current step. Do not exceed the budget.

### CONTEXT_REBUILD
Use when:
- manifest is missing/invalid/v1/duplicated;
- task scope materially changed;
- base/rebase invalidated the prior neighborhood;
- previous targets are no longer relevant;
- changed-file ratio exceeds configured threshold;
- saved context exceeds the hard budget.

## Bounded load order
1. explicit targets;
2. current PR changed files;
3. direct dependencies;
4. direct consumers;
5. related tests/config/contracts;
6. framework/runtime relationships only when evidence requires them.

Never load the whole repository by default.

## Output
Return context state, selected PR/head SHA, files loaded, stale references refreshed, budget usage, restored security classification/evidence freshness, and remaining uncertainty.
