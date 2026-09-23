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
