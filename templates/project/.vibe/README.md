# .vibe project contract

These files contain stable project-level routing context for ChatGPT Web.

- `config.json` — hard context limits, manifest version and verification defaults.
- `project-context.json` — detected languages, frameworks, entrypoints and verification commands.

Per-task state lives in the task pull request body, not on the default branch. The schema-v2 task manifest stores paths, symbols, GitHub blob SHAs, roles, discovery depth, acceptance evidence and verification head binding. It never stores source copies.
