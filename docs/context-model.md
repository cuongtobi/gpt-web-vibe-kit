# Context model

## Three layers

### 1. Stable project context
Read from the target repository:
- `AGENTS.md`
- `.vibe/config.json`
- `.vibe/project-context.json`

### 2. Task context
Read from the active pull request body:
- request and mode;
- targets and symbols;
- direct dependencies;
- reverse dependencies / consumers;
- tests and config;
- observed GitHub blob SHAs;
- acceptance criteria;
- verification state.

### 3. Live context
Fetched fresh from GitHub:
- current bounded source;
- current PR diff;
- current branch/base SHAs;
- current CI/check results;
- review comments when relevant.

## Context decisions

`CONTEXT_HIT`
: All observed references still have the stored blob SHA and scope is unchanged.

`CONTEXT_REFRESH`
: A bounded minority of observed files changed. Refresh those files and their immediate dependency/consumer neighborhood.

`CONTEXT_REBUILD`
: Context is missing, scope changed, the baseline changed materially, or too much of the observed neighborhood changed.

## Why PR body is task storage
A shared pointer on `main` cannot safely represent concurrent tasks. A PR already owns one branch/head SHA, one diff, one CI history, one discussion and one merge lifecycle, so it is the natural task container.
