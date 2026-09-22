---
name: verify
description: Verifies acceptance criteria, diff safety and current-head CI evidence before a task can be called complete.
---

# Verify

## Goal
Produce evidence that belongs to the current PR head and maps to the task's acceptance criteria.

## Procedure
1. Read current task manifest, current PR head SHA and changed-file diff.
2. Confirm manifest context is not stale. Refresh if needed.
3. Determine established verification commands from project context/manifests.
4. If no meaningful check is configured, report `NEEDS_VERIFICATION_CONFIG`; never add a no-op command to obtain a pass.
5. Inspect current-head workflow/check runs.
6. When a job fails, inspect its steps/logs and route code failures back to build.
7. Review the final diff for:
   - requested behavior;
   - unintended scope;
   - public/config/schema compatibility;
   - error/edge handling;
   - missing consumers;
   - framework/dynamic dependencies not represented by static search.
8. Map every AC item to actual evidence.

## Status
`PASS_VERIFIED`
: required meaningful checks actually ran and passed for the current head, and required acceptance criteria are met.

`FAIL_VERIFICATION`
: a required check failed, behavior is wrong, or current code changed after the evidence.

`NEEDS_VERIFICATION_CONFIG`
: no meaningful executable/project CI evidence is configured.

## Current-head rule
A workflow run for SHA A is stale after the PR moves to SHA B. Do not report PASS based on SHA A.

## Static graph rule
A clean static dependency neighborhood cannot prove dynamic framework wiring is unaffected. Use native tooling/tests/direct checks when relevant.

## PR update
Write current head SHA, CI/run identifiers, verification status and acceptance evidence back to the task manifest.
