---
name: github-review
description: Uses GitHub PR metadata, the strict v2 manifest, diff, reviews and current-head CI as the durable handoff layer.
---

# GitHub Review

## Goal
Make the pull request a complete durable handoff for the task.

## Procedure
1. Confirm intended head/base.
2. Require exactly one valid schema-v2 task manifest block.
3. Confirm manifest task `head_sha` matches the current PR head.
4. Confirm saved context is inside `.vibe/config.json` hard budgets.
5. Ensure human-readable PR text summarizes goal, scope, compatibility, checks and unresolved risks.
6. Read current diff/current-head CI and relevant unresolved review threads.
7. Review touched comments/docstrings/documentation for useful rationale, redundancy and staleness.
8. Confirm final security classification from the diff. For a security-sensitive task, require non-empty structured `security.evidence`, `security.head_sha == current PR head`, and explicit limitations/scanner availability; normal PASS evidence alone is insufficient.
9. If code changes after verification/review, update head state, invalidate stale verification/security evidence and re-verify.
10. Mark task `ready` only when required ACs are met, `verification.head_sha` equals current PR head, and any required security evidence is current.
11. Merge only with explicit user authorization or clear repository authorization.

## Handoff
A future session should recover from:
```text
project contract
+ PR metadata/body
+ schema-v2 bounded references/symbols
+ current source/diff
+ current-head CI/reviews
```

Old chat history is not required.
