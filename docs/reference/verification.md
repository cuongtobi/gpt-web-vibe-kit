# Verification and completion reference

Verification evidence is valid only for the exact current PR head.

```text
verification.head_sha == task.head_sha == current PR head SHA
```

Supported verification statuses:

- `PASS_VERIFIED`
- `FAIL_VERIFICATION`
- `NEEDS_VERIFICATION_CONFIG`

## PASS requirements

A pass requires:

- meaningful project-native checks for the current head;
- every acceptance criterion is `met` with non-empty structured evidence;
- required verification commands are present when configured;
- security/frontend completion requirements are satisfied when applicable.

Run the completion gate before declaring a task ready:

```bash
python runtime/vibe_web.py completion-status task.json --config .vibe/config.json
```

Any new commit makes saved head-bound verification stale. Previously ready/complete work returns to verification until new evidence is produced.

Generic prose such as “tests passed” is not structured acceptance evidence.
