---
name: build
description: Implements the planned GitHub change with minimal scope while keeping the v2 PR task manifest current.
---

# Build

## Goal
Implement the planned behavior with the smallest correct and reviewable diff.

## Before editing
1. Confirm current PR head and schema-v2 task manifest.
2. Re-run session refresh if referenced files changed.
3. Confirm current context remains within the hard budget.
4. Read only the target/dependency/consumer/test files required for implementation.
5. Preserve unrelated changes.

## Behavioral implementation policy

- Implement the minimum code that satisfies the accepted behavior and constraints. Do not add speculative features, future-proofing layers, or configurability that is not required by the task.
- Prefer an existing direct pattern over a new abstraction when the abstraction has only one current use and no concrete boundary, variation, reuse, or testing need.
- Add defensive/error handling for plausible states under established contracts. Do not create branches for states that are provably impossible solely to appear defensive.
- Make surgical changes: do not refactor, rename, reformat, comment-clean, or delete unrelated existing code. If unrelated dead/problematic code is discovered, report it instead of folding it into the patch.
- Clean up imports, variables, helpers, tests, or files made obsolete by **this change**; do not treat pre-existing cleanup as implicitly authorized.
- Match established project style even when another style would also be reasonable.
- Every changed line should be explainable by the request, an acceptance criterion, a regression test, a compatibility/security requirement, or cleanup made necessary by this patch. If it cannot be traced to one of those, remove it or explicitly re-plan the scope.
- If implementation grows materially beyond the planned shape, revisit the plan before continuing rather than normalizing the extra complexity after the fact.

## Frontend tasks

When the manifest carries `frontend`, or current evidence clearly shows UI work that planning missed, read `../vibe/reference/frontend-policy.md` before the first UI edit and update the manifest classification if needed. Preserve-versus-redesign intent is a scope constraint. Reuse the incumbent design system, read optional `DESIGN.md` when present, and implement only materially relevant frontend acceptance dimensions. Do not introduce a separate design workflow or install visual tooling merely because frontend policy applies.

## Comment and documentation policy
- Prefer names and structure that make code self-explanatory.
- Comment **why**, invariants, constraints, tradeoffs and deliberate workarounds; do not narrate obvious statements, assignments, branches or calls.
- Document public/shared APIs and non-obvious modules/functions when callers need contracts, side effects, errors, lifecycle or invariants.
- Preserve useful rationale comments; update or remove them if behavior changes.
- Keep TODO/FIXME actionable and specific.
- Follow existing project-native comment/docstring conventions when compatible with these rules.

## Security policy
If the plan marks the task security-sensitive, or implementation reveals a sensitive surface the plan missed, update the manifest classification and apply the relevant controls before continuing.

General rules:
- preserve authentication, authorization, validation, isolation and secret-handling controls unless the requested contract explicitly changes them;
- prefer framework-native security mechanisms and safe defaults over custom security code;
- validate at trust boundaries, encode/escape at the output sink, use least privilege and fail closed for access decisions;
- never hardcode, expose or log secrets, raw passwords, access/refresh tokens, session identifiers, private keys or payment credentials;
- do not invent cryptography, password hashing, token formats or random-token generation when established primitives exist;
- avoid shell execution with user-controlled strings; prefer structured arguments/safe APIs;
- avoid dynamic database queries from untrusted input when parameterized/native query APIs are available;
- do not disable CSRF, XSS/output encoding, SSRF restrictions, authorization, TLS/certificate checks, cookie protections or upload restrictions for convenience;
- add focused negative/abuse-case tests for changed security properties when feasible.

Surface prompts to assess when applicable:
- auth/session/token/password: rotation/expiry, revocation, replay, fixation, cookie flags, credential storage, authorization, brute-force/rate-limit behavior in scope, sensitive logging;
- file upload/filesystem: size, MIME/extension, traversal, filename normalization, overwrite, executable content, storage boundary, symlinks when relevant, authorization;
- database/user input: parameterization, injection, unsafe dynamic identifiers, mass assignment, tenant/row ownership, integrity/transaction boundaries;
- user-controlled URL/network fetch: scheme/host restrictions, redirects, internal/private network reachability, credential forwarding, SSRF behavior, response/time limits;
- HTML/template rendering: contextual encoding, unsafe HTML bypasses, script/URL injection, template injection, applicable CSRF/CSP behavior;
- command/process execution: shell avoidance, argument separation, executable selection, environment/path/working-directory/privilege boundary;
- payments/webhooks: server-side amount/currency authority, idempotency, authorization, signature verification, replay and state transitions;
- secrets/credentials: source-control exposure, logs/errors/telemetry, storage, rotation/revocation, least privilege and client-side exposure.

## Rules
- Follow existing project patterns.
- Avoid speculative abstractions and unrelated cleanup.
- Do not silently break APIs/config/schemas/persisted data/wire formats.
- Update focused tests with behavior changes.
- Expand context only for concrete evidence and never beyond configured hard limits.
- When scope cannot fit safely, split the task/PR instead of bypassing the budget.

## `test` mode
Prefer test-only changes. Production behavior changes require explicit task scope.

## `docs` mode
Change docs/examples/metadata and only the minimum source/config needed to keep documentation accurate.

## After editing
1. Review the diff.
2. Refresh paths, symbols, roles, depths and blob SHAs.
3. Update manifest `head_sha`.
4. A changed head invalidates older `PASS_VERIFIED` evidence, any `security.evidence` bound to an older security `head_sha`, and any `frontend.visual_qa.evidence` bound to an older frontend visual-QA `head_sha`.
5. Set task status to `verifying`.
6. Hand off to `verify`.

Implementation is not verification.
