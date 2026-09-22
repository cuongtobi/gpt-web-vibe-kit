# .vibe project contract

These files contain stable project-level context for ChatGPT Web.

- `config.json` — workflow limits and verification commands.
- `project-context.json` — small stable summary: languages, frameworks, entrypoints, commands and architecture facts.

Per-task state does **not** live here. It lives in the task pull request body so concurrent tasks do not overwrite each other.

The PR task manifest stores references (paths, symbols, GitHub blob SHAs, consumers and tests), not copies of source content.
