# Task manifest reference

Each vibe-managed task pull request contains **exactly one** schema-v2 manifest block in the PR body.

```text
<!-- gpt-web-vibe:task:start -->
{ ...schema-v2 JSON... }
<!-- gpt-web-vibe:task:end -->
```

Human-readable PR text may appear outside the block.

## Main sections

- task identity: `task_id`, `mode`, `status`, request and base/head refs;
- `targets`: files directly in scope;
- `context`: symbols, dependencies, consumers, tests, config and observed blob SHAs;
- `acceptance`: observable criteria with structured evidence;
- `verification`: commands, current evidence head, CI run and status;
- optional `frontend`: UI intent, acceptance bindings and visual-QA state;
- optional/backward-compatible `security`: classification, surfaces, controls, evidence and limitations;
- `uncertainties`: unresolved facts that matter.

## Key invariants

- duplicate or mismatched manifest markers are invalid;
- schema v1 is not normal continuation state;
- referenced context files must appear in `observed_files`;
- acceptance IDs are unique;
- `PASS_VERIFIED` requires every acceptance item to be `met` with evidence;
- `ready` and `complete` require a current pass;
- head-bound evidence must match the current task/PR head.

The machine definition is `schemas/task.schema.json` plus `runtime/state.py`. Those files win over prose if documentation drifts.
