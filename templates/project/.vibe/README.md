# .vibe project contract

These files contain stable project-level routing context for ChatGPT Web.

- `config.json` — hard context limits, manifest version and verification defaults.
- `project-context.json` — detected languages, frameworks, entrypoints and verification commands.

Per-task state lives in the task pull request body, not on the default branch. The schema-v2 task manifest stores paths, symbols, GitHub blob SHAs, roles, discovery depth, acceptance evidence and verification head binding. It never stores source copies.


The source kit also defines Comment & Documentation Policy and Security Policy. New task manifests include a `security` object so security classification, surfaces and current-head evidence can survive across ChatGPT Web sessions. Older schema-v2 manifests without this optional field remain readable for compatibility, but an active security-sensitive task should add it before verification.
