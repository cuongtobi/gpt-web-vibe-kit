# Pull request task contract — schema v2

Every vibe-managed task PR must contain **exactly one** machine-readable block:

```text
<!-- gpt-web-vibe:task:start -->
```json
{
  "schema_version": 2,
  "task_id": "refresh-token-expiry",
  "mode": "bug_fix",
  "status": "building",
  "request": "Fix refresh token after the session expires.",
  "base_branch": "main",
  "base_sha": "<sha>",
  "head_branch": "vibe/bug_fix/refresh-token-expiry",
  "head_sha": "<sha>",
  "targets": ["app/services/auth_service.py"],
  "context": {
    "symbols": ["refresh_access_token", "decode_refresh_token"],
    "dependencies": ["app/security/token.py"],
    "consumers": ["app/api/auth.py"],
    "tests": ["tests/test_auth.py"],
    "config_files": [],
    "observed_files": [
      {
        "path": "app/services/auth_service.py",
        "sha": "<blob-sha>",
        "role": "target",
        "depth": 0,
        "symbols": ["refresh_access_token"]
      },
      {
        "path": "app/security/token.py",
        "sha": "<blob-sha>",
        "role": "dependency",
        "depth": 1,
        "symbols": ["decode_refresh_token"]
      },
      {
        "path": "app/api/auth.py",
        "sha": "<blob-sha>",
        "role": "consumer",
        "depth": 1,
        "symbols": []
      },
      {
        "path": "tests/test_auth.py",
        "sha": "<blob-sha>",
        "role": "test",
        "depth": 1,
        "symbols": ["test_refresh_after_access_expiry"]
      }
    ]
  },
  "acceptance": [
    {
      "id": "AC1",
      "expected": "Expired access can be refreshed with a valid refresh token.",
      "status": "pending",
      "evidence": []
    }
  ],
  "verification": {
    "commands": ["pytest tests/test_auth.py"],
    "head_sha": null,
    "ci_run_id": null,
    "status": null
  },
  "security": {
    "classification": "security-sensitive",
    "surfaces": ["authentication/session/token"],
    "trust_boundaries": ["refresh token -> session renewal"],
    "abuse_cases": ["replay revoked refresh token"],
    "controls": ["rotation", "revocation", "authorization boundary", "sensitive-token logging protection"],
    "evidence": [],
    "head_sha": null,
    "limitations": []
  },
  "uncertainties": []
}
```
<!-- gpt-web-vibe:task:end -->
```

Human-readable PR text may appear outside the block.

## Required invariants

1. There is exactly one start marker and one end marker.
2. `schema_version` is `2`.
3. `base_branch`, `base_sha`, `head_branch` and task `head_sha` are non-empty.
4. Modes are:
   - `feature`
   - `change`
   - `bug_fix`
   - `refactor`
   - `hotfix`
   - `test`
   - `docs`
5. Every path referenced by targets/dependencies/consumers/tests/config must appear in `observed_files`.
6. Every observed file has:
   - `path`
   - current GitHub blob `sha`
   - primary `role`
   - non-negative discovery `depth`
   - relevant `symbols`
7. Acceptance IDs are unique.
8. Acceptance evidence is a structured list of `{type, ref}` objects.
9. `PASS_VERIFIED` requires `verification.head_sha == task.head_sha`.
10. The saved context must fit the target repository's `.vibe/config.json` hard budget.
11. `security` is optional at the schema level only for backward compatibility with older schema-v2 PRs. New tasks should include it.
12. A `security-sensitive` manifest must identify at least one security surface.
13. If a security-sensitive task is `PASS_VERIFIED`, `security.head_sha` must equal task `head_sha` and `security.evidence` must be non-empty.

## Acceptance evidence examples

Test evidence:

```json
{
  "type": "test",
  "ref": "tests/test_auth.py::test_refresh_after_access_expiry"
}
```

CI evidence:

```json
{
  "type": "ci",
  "ref": "run:123456789"
}
```

Diff/source evidence:

```json
{
  "type": "source",
  "ref": "app/services/auth_service.py"
}
```

Evidence describes where a criterion was demonstrated; it is not a replacement for actual current-head verification.

## Security evidence

Security state is durable task state, not a claim that the code is secure.

Typical evidence records:

```json
{
  "type": "security-test",
  "ref": "tests/test_auth.py::test_revoked_refresh_token_cannot_be_replayed"
}
```

```json
{
  "type": "security-review",
  "ref": "diff:auth-session-token-review@<head-sha>"
}
```

```json
{
  "type": "dependency-audit",
  "ref": "ci:run:123456789/job:dependency-audit"
}
```

When tooling is unavailable, record the limitation in `security.limitations`; do not invent scanner evidence. A new head invalidates prior `security.head_sha` and evidence just as it invalidates prior PASS evidence.

## Verification head binding

Before verification:

```json
{
  "head_sha": "<current-task-head>",
  "verification": {
    "head_sha": null,
    "ci_run_id": null,
    "status": null
  }
}
```

After current-head verification:

```json
{
  "head_sha": "abc123",
  "verification": {
    "head_sha": "abc123",
    "ci_run_id": 123456789,
    "status": "PASS_VERIFIED"
  }
}
```

After a new commit moves the task to `def456`, the old PASS is stale and must not remain a valid pass.

## Updating the block

Update the block whenever any of these materially changes:

- task scope or mode;
- target paths/symbols;
- dependencies/consumers/tests/config;
- observed blob SHAs, roles or depths;
- head SHA;
- acceptance evidence/status;
- verification evidence/status;
- uncertainties.

## Schema v1

Schema v1 is intentionally not accepted as normal v2 state. For an old active PR:

1. read current PR/base/head;
2. rediscover the bounded current neighborhood;
3. add roles/depths/symbols;
4. convert acceptance evidence to the structured list;
5. add `verification.head_sha`;
6. replace the old block with one valid schema-v2 block.

Do not copy stale v1 references forward without checking current GitHub state.
