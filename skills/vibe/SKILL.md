---
name: vibe
description: Orchestrates an end-to-end GitHub-native code change on ChatGPT Web through session, plan, build, verify and GitHub review.
---

# Vibe

## Goal
Complete one repository change with bounded context and evidence tied to the current GitHub head.

## Procedure
1. Apply `session`.
2. Classify the request as `feature`, `change`, `bug_fix`, `refactor`, `hotfix`, `test`, or `docs`.
3. For a new objective:
   - create a configured `vibe/` branch;
   - create a schema-v2 task manifest;
   - open a PR early enough that its body becomes durable task state.
4. Apply `plan`.
5. Unless planning-only, apply `build`.
6. Apply `verify`.
7. Apply `github-review`.
8. Keep manifest paths/symbols/blob SHAs/head/verification synchronized.

## Mode intent
- `test`: test-only/coverage work without production behavior change unless explicitly requested.
- `docs`: README/docs/examples/metadata work with minimal code context.
- other modes follow their normal behavior/compatibility semantics.

## Invariants
Bug:
```text
REPRODUCE -> ROOT CAUSE -> REGRESSION TEST -> MINIMAL FIX -> AFFECTED CHECKS -> VERIFY
```

Refactor:
```text
BASELINE -> TARGET -> DIRECT CONSUMERS -> REFACTOR -> OLD-REFERENCE SEARCH -> VERIFY
```

## Constraints
- No continuity may depend on chat memory.
- Strictly use one schema-v2 manifest block per task PR.
- Respect hard context budgets.
- Never use old CI as proof for a newer head.
- Never infer absence of impact from one empty static search.
- Do not silently broaden scope.
- Do not merge without explicit authorization or repository rules that clearly authorize it.
