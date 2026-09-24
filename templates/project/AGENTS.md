# ChatGPT Web + GitHub project instructions

This project uses `cuongtobi/gpt-web-vibe-kit`.

## Workflow
```text
session -> plan -> build -> verify -> github-review
```

Do not depend on old chat history. Read `AGENTS.md`, `.vibe/config.json`, `.vibe/project-context.json`, then the selected PR's single schema-v2 task manifest. Fetch only the bounded current GitHub neighborhood needed for the task.

The limits in `.vibe/config.json` are hard limits. Do not bypass them by loading more source; reduce or split scope when needed.

Use iterative symbol-aware GitHub search: direct evidence -> candidate files -> relevant symbols -> direct dependencies/consumers/tests. Persist references and blob SHAs, not source copies.

Static dependency discovery is advisory. Dynamic framework wiring requires project-native tests/tooling or direct inspection.

Never report `PASS_VERIFIED` unless `verification.head_sha`, task `head_sha` and the current PR head SHA all match.


## Comment and documentation policy

Prefer self-explanatory code. Comment **why**, constraints, invariants and non-obvious tradeoffs; do not narrate obvious code. Document public/shared contracts when useful, keep TODO/FIXME actionable, and update/remove stale comments or docstrings whenever touched behavior changes.

## Security policy

This workflow does not guarantee secure code. Its rule is: **security-sensitive changes cannot silently pass without explicit security review/evidence**.

Treat authentication, authorization, session/token/password, upload/filesystem, user-controlled database queries or URLs, HTML/template rendering, command execution, payment/webhook and secrets/credentials work as security-sensitive. Record the affected trust boundary in the PR task manifest, apply relevant secure-coding controls, and require current-head security evidence before the task is ready.
