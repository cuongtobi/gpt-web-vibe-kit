---
name: github-review
description: Uses GitHub PR metadata, diff, review threads and CI as the durable handoff and final review layer for a vibe task.
---

# GitHub Review

## Goal
Make the pull request a complete durable handoff for the task.

## Procedure
1. Confirm the PR points from the intended vibe branch to the intended base.
2. Ensure the task manifest block exists exactly once and is valid.
3. Ensure human-readable PR text summarizes:
   - goal;
   - main files/areas changed;
   - compatibility notes;
   - tests/checks;
   - unresolved risks.
4. Read the current diff and current-head CI.
5. Read unresolved review threads/comments when they can affect correctness.
6. If code changes after review/verification, update manifest head SHA and re-verify.
7. Mark status `ready` only when required acceptance criteria and current-head verification are satisfied.
8. Merge only with explicit user authorization or repository rules that clearly authorize it.

## Handoff
A future session should be able to recover the task from:
```text
PR metadata/body
+ branch/head
+ bounded manifest references
+ current source
+ diff
+ CI/reviews
```
without reading old chat history.
