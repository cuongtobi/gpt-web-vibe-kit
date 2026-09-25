---
name: vibe
description: Orchestrates an end-to-end GitHub-native code change on ChatGPT Web through session, plan, build, verify and GitHub review.
---

# Vibe

## Goal
Complete one repository change with bounded context and evidence tied to the current GitHub head.

## Behavioral orchestration

- Convert the request into observable goals before implementation; each non-trivial step should have a corresponding check or evidence source.
- Surface materially consequential assumptions early. Do not interrupt autonomous execution for minor, reversible ambiguity that can be handled with a stated conservative assumption.
- Prefer the simplest scoped solution that satisfies the acceptance criteria; complexity must be justified by an actual constraint, boundary, or verified need.
- Keep retries evidence-driven: diagnose -> change -> re-check. Do not churn through rewrites without new evidence.

## Procedure
1. Apply `session`.
2. Classify the request as `feature`, `change`, `bug_fix`, `refactor`, `hotfix`, `test`, or `docs`.
3. For a new objective:
   - create a configured `vibe/` branch;
   - create a schema-v2 task manifest;
   - open a PR early enough that its body becomes durable task state.
4. Apply `plan`. The plan must classify whether the task is frontend from request/target evidence and, when applicable, persist the optional manifest `frontend` state without adding a new workflow. It must also classify the task as `standard` or `security-sensitive`; sensitive tasks persist surfaces/trust boundaries/abuse cases/controls in manifest `security` state.
5. Unless planning-only, apply `build`.
6. Apply `verify`. A security-sensitive task is not complete merely because normal current-head checks pass; its security evidence must also be current and complete.
7. Apply `github-review`.
8. Keep manifest paths/symbols/blob SHAs/head/verification/frontend visual evidence/security evidence synchronized.

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
- Do not claim that the kit or a completed task is "security guaranteed"; report concrete security evidence and limitations instead.
