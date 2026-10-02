# Test-only work

Mode: `test`.

Use this for regression tests, coverage improvements or additional edge-case checks without changing production behavior by default.

## Context

```text
production target
-> current behavior/contract
-> existing test harness/helpers
-> important edge cases
```

If a test reveals an out-of-scope production bug, report it instead of silently fixing production code.

## Prompt

```text
@GitHub work with <owner>/<repo>.
Use cuongtobi/gpt-web-vibe-kit.

Mode: test

Add tests for:
<module/behavior>

Cover:
- happy path;
- important invalid/error cases;
- regression-prone edge cases.

Do not change production behavior unless explicitly requested.
```
