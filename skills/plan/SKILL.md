---
name: plan
description: Discovers a bounded symbol-aware target/dependency/consumer/test neighborhood and records an evidence-mapped plan in the task PR.
---

# Plan

## Goal
Find the smallest safe change and persist enough current references for another ChatGPT Web session to resume.

## Behavioral planning rules

- Surface assumptions that materially affect the solution; do not silently choose between materially different interpretations.
- Ask only when unresolved ambiguity can change behavior, public contracts, persisted data, security, compatibility, destructive effects, or task scope. For minor/reversible ambiguity, state the conservative assumption and proceed.
- When a materially simpler approach satisfies the same acceptance behavior, prefer it and record the tradeoff instead of silently choosing a more elaborate design.
- Do not turn uncertainty into speculative scope. Unknowns become explicit uncertainties/evidence gaps, not extra features or abstractions.
- Express non-trivial implementation steps as **step -> verification evidence** so build and verify know what success means.

## Iterative symbol-aware retrieval
Use GitHub search in bounded rounds; do not rely on filenames alone.

### Round 1 — direct evidence
Search exact:
- error/trace text;
- route/API/config keys;
- user-provided identifiers;
- strong request keywords.

Fetch only promising files.

### Round 2 — symbol expansion
From fetched candidates:
1. identify relevant classes/functions/types/constants/modules;
2. add high-confidence identifiers to `context.symbols`;
3. search those symbols and import/module specifiers;
4. identify the exact target.

### Round 3 — neighborhood expansion
Search:
- imports/requires used by the target;
- direct consumers/usages of target symbols/modules;
- related tests;
- config/schema/API/framework registrations.

Stop earlier when the target and required neighborhood are clear. Respect `max_search_rounds`, `max_symbol_hints` and every hard context budget in `.vibe/config.json`.

If one scoped search returns no result, try another evidence-supported term. An empty search never proves no impact.

## Persisted task context
For every loaded task-relevant file, persist:
- current path;
- current GitHub blob SHA;
- primary `role`;
- discovery `depth`;
- relevant `symbols`.

Also persist the task-wide high-confidence identifiers in `context.symbols`. Do not store source copies or speculative symbols.

## By mode

### `bug_fix`
symptom -> reproduce/locate -> target/root cause -> regression test -> smallest fix.

### `refactor`
explicit target -> all reasonably findable direct consumers -> tests/contracts -> baseline invariants.

### `feature` / `change`
desired behavior -> public/config/data contracts -> implementation neighborhood -> tests.

### `test`
focus on production target + existing test harness + edge cases. Do not change production behavior unless requested or a separately scoped bug is accepted.

### `docs`
focus on documentation targets and source/config needed to verify claims. Avoid code dependency expansion that is irrelevant to documentation.

## Security classification
Classify every task from both the request and discovered impact as `standard` or `security-sensitive`.

Treat the task as security-sensitive when it touches authentication, authorization, sessions, tokens, passwords, file upload/filesystem access, database queries using user-controlled data, user-controlled URLs/network fetches, HTML/template rendering, command/process execution, payments/webhooks, secrets/credentials, or another comparable trust boundary.

For a security-sensitive task, persist/update manifest `security` with:
- `classification: "security-sensitive"`;
- concrete `surfaces`;
- relevant `trust_boundaries`;
- plausible `abuse_cases`;
- existing/security `controls` that must remain intact;
- empty/stale verification `evidence` until verify runs on the current head;
- `head_sha: null` until security evidence is produced;
- known `limitations`.

Examples:
- refresh-token/session work: rotation/expiry, revocation, replay risk, cookie flags, session fixation, authorization boundary and secret/token logging;
- file upload work: size limits, extension/MIME validation, path traversal, filename sanitization, overwrite behavior, execution risk, storage boundary and authorization.

If an older valid schema-v2 task lacks `security`, it remains readable for compatibility. Add the block when the task is planned/continued under this policy. Do not call a task secure merely because it was classified.

## Acceptance
Use stable IDs such as AC1. Each criterion contains an observable expected result, status and structured evidence list. Use `unverified`/empty evidence until real evidence exists.

## Output
Summarize material assumptions/tradeoffs, targets/symbols, bounded neighborhood, budget usage, ordered steps with verification evidence, security classification/evidence plan, and uncertainties.
