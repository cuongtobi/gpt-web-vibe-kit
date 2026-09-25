# Context model

`gpt-web-vibe-kit` is designed for ChatGPT Web + GitHub. It intentionally avoids a persistent local checkout, external vector database or long-lived context service.

## 1. Stable project context

Read from the target repository:

- `AGENTS.md`
- `.vibe/config.json`
- `.vibe/project-context.json`

This layer contains durable routing facts: project stack, important entrypoints, verification commands and hard context limits. It must stay small.

## 2. Task context

Stored in exactly one schema-v2 block in the active pull request body:

- request, mode and task status;
- base/head branch and SHA;
- target paths;
- `context.symbols`;
- direct dependencies and consumers;
- tests and config files;
- observed file path/blob SHA/role/depth/symbols;
- acceptance criteria and structured evidence;
- verification commands/status/head SHA;
- uncertainties.

The task manifest stores references, not source copies.

## 3. Live context

Fetched fresh from GitHub:

- current bounded source;
- current PR diff;
- current base/head SHA;
- current CI/check results;
- relevant unresolved review discussion.

Live GitHub state is authoritative over historical manifest references.

## Hard context budget

`.vibe/config.json` defines enforced limits. Default v2 values:

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

The manifest makes budget usage auditable by recording for each observed file:

```json
{
  "path": "app/services/auth.py",
  "sha": "<blob-sha>",
  "role": "target",
  "depth": 0,
  "symbols": ["refresh_access_token"]
}
```

Roles:

- `target`
- `dependency`
- `consumer`
- `test`
- `config`
- `related`

Depth 0 is the explicit target/current anchor. Direct relationships are normally depth 1. The runtime refuses to treat over-budget state as a normal context hit.

If a task cannot fit safely inside the configured limits, reduce or split task scope instead of expanding context indefinitely.

## Context decisions

### `CONTEXT_HIT`

Use when:

- schema-v2 manifest is valid and unique;
- task scope/baseline is unchanged;
- observed blob SHAs still match;
- context remains inside the hard budget.

Only fetch current content needed for the immediate step.

### `CONTEXT_REFRESH`

Use when:

- task identity/scope is still valid;
- only a bounded minority of observed files changed;
- refresh can stay inside budget.

Refresh changed references plus directly required target/dependency/consumer/test relationships and update blob SHAs.

### `CONTEXT_REBUILD`

Use when:

- manifest is missing, duplicated, malformed or schema v1;
- scope materially changed;
- rebase/base changes invalidate the old neighborhood;
- old targets are no longer relevant;
- changed ratio exceeds `rebuild_changed_ratio`;
- saved context exceeds hard limits.

A rebuild does not mean reading the whole repository. It reruns bounded target discovery from current task evidence.

## Iterative retrieval model

Target discovery is symbol-aware but lightweight:

```text
round 1: exact errors/routes/identifiers/request terms
             ↓
         candidate files
             ↓
round 2: extract relevant symbols/import specifiers
             ↓
         symbol search
             ↓
round 3: direct dependencies/consumers/tests/contracts
             ↓
         bounded neighborhood
```

The plan may stop before round 3 when enough evidence exists. Empty search results never prove there is no impact.

Only high-confidence symbols are persisted in `context.symbols`. There is no project-wide source cache. Runtime retrieval can also return diagnostics (path, score, discovery round and request/symbol reasons). `max_search_rounds` and `max_symbol_hints` come from config, and bounded file scanning prioritizes shallower project paths before deep subtrees.

## Verification state

Task head and verification head are separate on purpose:

```json
{
  "head_sha": "<current task head>",
  "verification": {
    "head_sha": "<head that produced evidence>",
    "status": "PASS_VERIFIED"
  }
}
```

A pass is current only when:

```text
verification.head_sha == task.head_sha == current PR head SHA
+ every acceptance criterion is met with structured evidence
+ required security/frontend evidence is current
```

The config-aware completion gate also enforces `verification.require_commands` and explicit disposition for runtime security candidates kept as standard. When code changes, every saved verification outcome becomes stale; ready/complete state returns to verification.

## Why the PR body is task storage

A shared `current-task.json` on `main` cannot safely represent concurrent work. A PR naturally owns:

- one branch/head;
- one diff;
- one CI history;
- one review lifecycle;
- one merge lifecycle.

Therefore one PR is the durable task container and the repository remains free of per-task history files.
