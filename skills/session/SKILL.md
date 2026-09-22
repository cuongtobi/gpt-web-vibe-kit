---
name: session
description: Restores bounded project and task context from GitHub at the start of a new ChatGPT Web session.
---

# Session

## Goal
Reconstruct enough current context to continue safely without loading the whole repository or depending on previous chat history.

## Bootstrap order
1. Read target `AGENTS.md`.
2. Read `.vibe/config.json` and `.vibe/project-context.json` when present.
3. Resolve the task:
   - use an explicitly named PR/branch/task first;
   - when the user clearly says to continue and exactly one matching vibe PR exists, use it;
   - otherwise match open PRs by request/branch/title rather than guessing.
4. Read the selected PR metadata/body and parse the block between:
   - `<!-- gpt-web-vibe:task:start -->`
   - `<!-- gpt-web-vibe:task:end -->`
5. Read the current PR changed filenames/diff.
6. Validate observed file references by fetching their current GitHub blob SHAs from the PR head branch.

## Context decision

### CONTEXT_HIT
Use when:
- task scope is unchanged;
- observed file SHAs are unchanged.

Fetch current content only for the bounded referenced files needed for the immediate step.

### CONTEXT_REFRESH
Use when:
- only a bounded minority of observed files changed;
- branch/task identity is still the same.

Refresh changed files plus their direct imports/dependencies, direct consumers and related tests. Update the PR manifest references.

### CONTEXT_REBUILD
Use when:
- manifest is missing/invalid;
- task scope materially changed;
- base/rebase invalidated the prior neighborhood;
- most observed files changed;
- previous targets are no longer relevant.

Rediscover targets from the request, then rebuild the bounded neighborhood.

## Bounded load order
Prefer:
1. explicit targets;
2. changed files in the current PR;
3. direct dependencies;
4. direct consumers;
5. related tests/config/contracts;
6. framework/runtime relationships only when evidence requires them.

Respect `.vibe/config.json` limits. Never load every historical task or the entire repository as default context.

## Dependency rule
Static relationships are advisory. Search direct imports/requires/usages and framework registrations, but use native tests/analyzers for dynamic wiring.

## Output
Return the context state (HIT/REFRESH/REBUILD), selected task/PR/head SHA, files loaded, stale references refreshed, and remaining uncertainty.
