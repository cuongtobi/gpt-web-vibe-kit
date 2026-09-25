# gpt-web-vibe-kit contributor instructions

This repository is the source kit for a GitHub-native vibe-coding workflow designed for ChatGPT Web.

## Principles
- Public workflow: session -> plan -> build -> verify -> github-review.
- GitHub is durable task state; previous chat history is never required.
- Stable project context belongs in versioned project files; per-task context belongs in the task PR body.
- Persist references to code (paths, symbols, blob SHAs, tests, consumers), not source copies.
- Keep model context bounded and fetch current code from GitHub.
- Static dependency evidence is advisory; current source, native tooling, tests and CI are authoritative.
- Never claim PASS_VERIFIED without current-head runtime/CI evidence.
- Runtime code in this kit remains Python-standard-library-only.

## Source of truth
1. Current target-repository source/configuration.
2. Current task PR body, branch, diff and CI.
3. Target project context under `.vibe/`.
4. This kit's skill contracts.
5. Chat history and assumptions.

## Behavioral coding policy

Use these rules to reduce common LLM coding mistakes while preserving useful autonomy:

- **Think before coding.** State material assumptions and tradeoffs. If ambiguity can change behavior, public contracts, persisted data, security, compatibility, destructive effects, or task scope, ask before choosing silently. If ambiguity is minor, reversible, and low-risk, state the conservative assumption and proceed.
- **Simplicity first.** Implement the minimum code required for the accepted behavior. Do not add speculative features, single-use abstractions, or configurability that was not requested. Add defensive handling only for states that are plausible under established contracts; do not invent impossible failure modes.
- **Surgical changes.** Touch only what the task, its tests, compatibility/security requirements, or cleanup caused by the task actually require. Do not refactor, reformat, rename, or remove unrelated existing code. Match the repository's established style unless the task explicitly changes it.
- **Goal-driven execution.** Turn the request into observable acceptance criteria and map implementation steps to checks. For bugs, reproduce the failure when practical, fix the root cause, and verify the regression. For refactors, establish behavior before and after the structural change.
- **Changed-line traceability.** Every changed line should trace to the user request, an acceptance criterion, a required regression/compatibility/security check, or cleanup made necessary by this change.
- **Progress without churn.** Retry only when new evidence or a concrete change justifies another attempt. Do not repeatedly rewrite working code merely to make it look more sophisticated.

## Comment and documentation policy
- Prefer self-explanatory code; comments explain **why**, constraints, invariants or non-obvious tradeoffs rather than narrating obvious **what**.
- Add concise rationale for business rules, compatibility/framework constraints, security assumptions, performance/cache behavior, tricky algorithms, edge cases and deliberate workarounds.
- Document public/shared APIs and non-obvious modules/functions in the project's native style when callers or maintainers need contracts, side effects, errors, lifecycle or invariants. Avoid boilerplate docstrings for obvious private helpers.
- TODO/FIXME notes must be actionable and specific.
- When behavior changes, update or remove stale nearby comments/docstrings/docs.
- Do not add comments merely to increase comment density, repeat names or restate syntax.

## Security policy
The kit does not guarantee that generated or modified code is secure. Its enforceable goal is: **security-sensitive changes cannot silently pass without explicit security review/evidence**.

Treat a task as security-sensitive when the request or discovered impact touches authentication, authorization, sessions, tokens, passwords, file upload/filesystem access, database queries using user-controlled data, user-controlled URLs/network fetches, HTML/template rendering, command/process execution, payments/webhooks, secrets/credentials, or another comparable trust boundary.

For security-sensitive work:
- plan records security surfaces, trust boundaries, abuse/failure cases, controls to preserve and required evidence;
- build applies framework-native secure defaults, least privilege, trust-boundary validation/encoding and safe secret handling;
- verify performs an explicit security diff review, targeted security tests/checks, and project-native security/dependency scanning when available and relevant;
- security evidence is bound to the current PR head;
- normal lint/test/build or `PASS_VERIFIED` alone is not proof of security;
- never weaken authentication, authorization, validation, isolation or secret handling merely to make a check pass.

## Development
When behavior changes, update tests and both README variants.

```bash
python -m unittest discover -s tests -v
python -m py_compile install.py runtime/state.py runtime/vibe_web.py
```
