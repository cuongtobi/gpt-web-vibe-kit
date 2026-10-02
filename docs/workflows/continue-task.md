# Continue an existing task

Use this when a task already has a pull request or when moving to a new ChatGPT session.

## Prompt

```text
@GitHub continue PR #<number> in <owner>/<repo>.
Use cuongtobi/gpt-web-vibe-kit.
Restore context from the schema-v2 PR manifest before continuing.
```

## Restore order

```text
AGENTS.md
-> .vibe/config.json
-> .vibe/project-context.json
-> selected PR
-> schema-v2 manifest
-> current diff/head
-> observed blob SHA check
-> CONTEXT_HIT / CONTEXT_REFRESH / CONTEXT_REBUILD
-> bounded current files
-> current-head CI/reviews
```

Do not use old chat history as the primary continuation state.

If the PR number is unknown, identify the matching open task by task ID, branch, title or request. If multiple candidates remain, list them instead of guessing.
