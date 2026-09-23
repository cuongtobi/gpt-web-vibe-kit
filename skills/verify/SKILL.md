---
name: verify
description: Verifies acceptance criteria, diff safety and evidence tied explicitly to the current PR head SHA.
---

# Verify

## Goal
Produce meaningful evidence for the current PR head and map it to the task's acceptance criteria.

## Procedure
1. Read schema-v2 manifest, current PR head SHA and final diff.
2. Confirm context is current and within the hard budget.
3. Determine established verification commands from project context/manifests.
4. If no meaningful check exists, report `NEEDS_VERIFICATION_CONFIG`; never add a no-op check.
5. Inspect current-head workflow/check runs.
6. Route failed checks back to build only for evidence-supported root causes.
7. Review the final diff for requested behavior, unintended scope, compatibility, edge handling, missing consumers and dynamic framework wiring.
8. Map every acceptance item to structured evidence.

## Head binding
`verification.head_sha` is the commit SHA that produced the evidence.

`PASS_VERIFIED` is valid only when:

```text
verification.head_sha == task.head_sha == current PR head SHA
```

If the PR head changes, previous PASS evidence is stale and must not survive as a pass.

## Status
- `PASS_VERIFIED`: meaningful required checks passed for current head and required acceptance criteria are met.
- `FAIL_VERIFICATION`: required checks/behavior failed, or the implementation changed after relevant evidence.
- `NEEDS_VERIFICATION_CONFIG`: meaningful executable/project CI evidence is unavailable.

## PR update
Persist:
- current task `head_sha`;
- `verification.head_sha`;
- commands;
- CI run id when available;
- status;
- acceptance evidence.
