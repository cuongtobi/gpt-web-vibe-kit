---
name: vibe
description: Orchestrates an end-to-end GitHub-native code change on ChatGPT Web through session, plan, build, verify and GitHub review.
---

# Vibe

## Goal
Complete one repository change with bounded context and evidence tied to the current GitHub head.

## Procedure
1. Apply `session` first to restore project/task state.
2. Classify the request as `feature`, `change`, `bug_fix`, `refactor`, or `hotfix`.
3. If this is a new objective:
   - create a branch using the configured `vibe/` prefix;
   - build a task manifest from `templates/task.json`;
   - open a PR early enough that its body becomes durable task state.
4. Apply `plan`.
5. Unless the user explicitly requested planning only, apply `build`.
6. Apply `verify`.
7. Apply `github-review`.
8. Keep the PR task manifest synchronized when targets, context references, acceptance evidence, head SHA or verification status changes.

## Bug invariant
```text
REPRODUCE -> ROOT CAUSE -> FAILING REGRESSION TEST
-> MINIMAL FIX -> PASSING REGRESSION TEST -> AFFECTED CHECKS -> VERIFY
```

## Refactor invariant
Capture baseline behavior before structural edits. Discover reverse consumers, preserve public behavior/contracts, then verify against the current head.

## Constraints
- No task continuity may depend on chat memory.
- Never use old CI as proof for a newer head SHA.
- Never infer absence of impact from an empty static search.
- Do not silently broaden scope.
- Do not merge automatically unless the user has authorized merge or repository instructions explicitly permit it.
