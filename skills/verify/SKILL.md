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
7. Review the final diff for requested behavior, unintended scope, compatibility, edge handling, missing consumers and dynamic framework wiring. Enforce the behavioral policy:
   - every changed line traces to the request, an acceptance criterion, required regression/compatibility/security evidence, or cleanup caused by this patch;
   - no speculative feature, configurability, or abstraction was added without a concrete requirement;
   - no adjacent refactor, rename, reformat, or cleanup is mixed into the task merely because it was noticed;
   - error/edge handling covers plausible states under established contracts without invented defensive branches for provably impossible states.
8. Review comments/documentation in touched code: require rationale where non-obvious decisions would otherwise be misread; remove/reject comments that merely narrate code; confirm touched comments/docstrings/docs are not stale and TODO/FIXME notes are actionable.
9. Re-classify security from both the plan and the final diff. If either shows authentication, authorization, sessions, tokens, passwords, upload/filesystem, user-controlled database queries or URLs, HTML/template rendering, command/process execution, payments/webhooks, secrets/credentials or another comparable trust boundary, treat the task as security-sensitive even if planning missed it.
10. For every security-sensitive task, produce explicit current-head security evidence:
    - security-focused diff review against the recorded trust boundaries and abuse cases;
    - targeted negative/abuse-case tests or direct checks for affected security properties;
    - established project-native security scanner when available in the authorized environment;
    - ecosystem dependency-vulnerability check when dependencies/package changes or the affected surface make it relevant and the command is available;
    - explicit unavailable/not-configured notes for missing tooling and remaining limitations.
11. Map every acceptance item to structured evidence.

## Security evidence binding
For a security-sensitive task, update manifest `security` so:
- `classification` is `security-sensitive`;
- `surfaces`, `trust_boundaries`, `abuse_cases` and `controls` reflect the final diff;
- `evidence` contains structured `{type, ref}` records for the security diff review/tests/scanners/checks actually performed;
- `head_sha` equals the current PR head SHA;
- `limitations` records unavailable tooling or unverified assumptions.

Generic unit tests, lint, type checking, build success, a clean static dependency search or normal `PASS_VERIFIED` alone are not security evidence. Absence of a scanner does not automatically fail the task, but it must be explicit and the strongest feasible targeted evidence should be used. Never claim security is guaranteed.

## Head binding
`verification.head_sha` is the commit SHA that produced the evidence.

`PASS_VERIFIED` is valid only when:

```text
verification.head_sha == task.head_sha == current PR head SHA
```

If the PR head changes, previous PASS evidence is stale and must not survive as a pass.

## Status
- `PASS_VERIFIED`: meaningful required checks passed for current head and required acceptance criteria are met; when `security.classification == "security-sensitive"`, current-head `security.evidence` must also be present.
- `FAIL_VERIFICATION`: required checks/behavior failed, or the implementation changed after relevant evidence.
- `NEEDS_VERIFICATION_CONFIG`: meaningful executable/project CI evidence is unavailable.

## PR update
Persist:
- current task `head_sha`;
- `verification.head_sha`;
- commands;
- CI run id when available;
- status;
- acceptance evidence;
- security classification/evidence/head binding and limitations when the task carries `security` state.
