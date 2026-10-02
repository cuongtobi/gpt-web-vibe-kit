# Context and restore reference

The kit stores references to code, not cached source copies. Current source is fetched from GitHub when needed.

## Default hard limits

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

Configured values in `.vibe/config.json` are limits, not targets.

## Restore states

- `CONTEXT_HIT`: saved observed references are unchanged and budget-compliant.
- `CONTEXT_REFRESH`: a bounded minority changed; refresh only what is necessary.
- `CONTEXT_REBUILD`: scope/baseline changed materially, the manifest is stale/invalid, too much changed, or the saved neighborhood exceeds budget.

## Retrieval

Planning searches in bounded rounds:

```text
request/error/route evidence
-> promising files
-> relevant symbols/imports
-> direct dependencies/consumers/tests/config
-> stop when the safe neighborhood is clear or budget is reached
```

An empty search is not proof of no impact. If safe scope cannot fit, split/reduce the task instead of bypassing the budget.
