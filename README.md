# gpt-web-vibe-kit

[Tiếng Việt](README_vi.md) · [Detailed usage guide](docs/usage.md)

A GitHub-native vibe-coding kit for **ChatGPT Web + GitHub**, based on the workflow ideas from [my-vibe-kit](https://github.com/cuongtobi/my-vibe-kit) but redesigned for web sessions without a persistent local checkout.

```text
session -> plan -> build -> verify -> github-review
```

## Core idea
A new session does not reload the whole repository and does not require the previous chat. It reconstructs a bounded context from:

```text
AGENTS.md
+ .vibe/project-context.json
+ active task PR manifest
+ current PR diff
+ current relevant files
+ current-head CI
= working context
```

The task manifest stores **what to read**, not copies of everything previously read.

## State model
Stable project state lives in the target repository:

```text
AGENTS.md
.vibe/config.json
.vibe/project-context.json
```

Per-task state lives in the task PR body. This avoids a shared `current-task.json` on `main`, so multiple tasks can run concurrently.

The PR contains one machine-readable block:

```text
<!-- gpt-web-vibe:task:start -->
```json
{
  "schema_version": 1,
  "task_id": "jwt-refresh",
  "mode": "bug_fix",
  "status": "building",
  "request": "Fix refresh token after session expiry",
  "targets": ["app/services/auth.py"],
  "context": {
    "dependencies": ["app/security/token.py"],
    "consumers": ["app/api/auth.py"],
    "tests": ["tests/test_auth.py"],
    "config_files": [],
    "observed_files": [
      {"path": "app/services/auth.py", "sha": "<github-blob-sha>"}
    ]
  },
  "acceptance": []
}
```
<!-- gpt-web-vibe:task:end -->
```

## New-session bootstrap
The `session` skill:

1. Reads target `AGENTS.md`, `.vibe/config.json`, and `.vibe/project-context.json`.
2. Resolves the task from a specified PR/branch/task or the relevant open vibe PR.
3. Parses the PR task manifest.
4. Compares stored blob SHAs with current branch files.
5. Chooses:
   - `CONTEXT_HIT`: all observed references remain current.
   - `CONTEXT_REFRESH`: a bounded subset changed.
   - `CONTEXT_REBUILD`: scope/baseline changed materially, context is missing, or too much changed.
6. Fetches only the bounded target/dependency/consumer/test neighborhood.
7. Reads the current diff and latest CI.

## By task type

Bug fix:
```text
symptom -> symbol/file -> target -> dependencies -> consumers -> tests
        -> reproduce -> root cause -> regression test -> minimal fix
```

Refactor:
```text
target -> dependencies -> all discoverable direct consumers
       -> affected tests/contracts -> baseline -> refactor -> verify
```

## Skills
```text
skills/
├── bootstrap/SKILL.md
├── session/SKILL.md
├── vibe/SKILL.md
├── plan/SKILL.md
├── build/SKILL.md
├── verify/SKILL.md
└── github-review/SKILL.md
```

## Local project bootstrap
```bash
python install.py --target /path/to/project
python install.py --target /path/to/project --dry-run
```

The installer creates `.vibe/config.json`, `.vibe/project-context.json`, and `.vibe/README.md`. It creates `AGENTS.md` only if the target has none.

On ChatGPT Web, `bootstrap` creates the same contract directly through GitHub.

## ChatGPT Web usage
```text
@GitHub work with cuongtobi/sample-api.
Read cuongtobi/gpt-web-vibe-kit/skills/vibe/SKILL.md and use the workflow.
Fix refresh-token rotation after an expired session.
```

Continuation:
```text
@GitHub continue PR #42 in cuongtobi/sample-api using gpt-web-vibe-kit.
```

## Dependency model
Dependency discovery is bounded and repository-driven: inspect explicit imports/framework registrations, search symbol/import usage for consumers, apply language/framework adapter hints, then persist only references and GitHub blob SHAs in the PR manifest.

The dependency view is explicitly `static-best-effort / advisory`. Dynamic imports, DI, generated code/routes, macros, reflection, Rails/WordPress runtime wiring, bundler-only aliases and framework registries require native tools, tests, CI or direct inspection.

## Verification
Statuses:
- `PASS_VERIFIED`
- `FAIL_VERIFICATION`
- `NEEDS_VERIFICATION_CONFIG`

`PASS_VERIFIED` requires actual evidence for the current PR head SHA. Green CI from an older head is stale evidence.
