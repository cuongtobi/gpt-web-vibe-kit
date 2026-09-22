# Pull request task contract

Every vibe-managed task PR should contain exactly one machine-readable block:

```text
<!-- gpt-web-vibe:task:start -->
```json
{
  "schema_version": 1,
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
    "symbols": ["refresh_access_token"],
    "dependencies": ["app/security/token.py"],
    "consumers": ["app/api/auth.py"],
    "tests": ["tests/test_auth.py"],
    "config_files": [],
    "observed_files": [
      {
        "path": "app/services/auth_service.py",
        "sha": "<blob-sha>",
        "symbols": ["refresh_access_token"]
      }
    ]
  },
  "acceptance": [
    {
      "id": "AC1",
      "expected": "Expired access can be refreshed with a valid refresh token.",
      "evidence": "tests/test_auth.py::test_refresh_after_access_expiry",
      "status": "pending"
    }
  ],
  "verification": {
    "commands": ["pytest tests/test_auth.py"],
    "ci_run_id": null,
    "status": null
  },
  "uncertainties": []
}
```
<!-- gpt-web-vibe:task:end -->
```

Human-readable PR text may appear outside the block. Update the block when scope, bounded context, acceptance evidence, head SHA or verification status materially changes.
