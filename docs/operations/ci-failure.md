# CI failure

Treat a failing check as evidence, not as a reason to blindly retry.

## Flow

```text
failed run
-> failed job
-> failed step/log
-> root cause
-> scoped fix
-> new head
-> stale verification cleared
-> verify new head
```

If the failure is deterministic and actionable, fix the cause before rerunning. Retry only when the failure is plausibly transient.

A new commit invalidates verification evidence tied to the previous head.
