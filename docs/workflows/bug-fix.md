# Bug fix

Mode: `bug_fix`.

Use this when observed behavior is defective.

## Required discipline

```text
REPRODUCE / LOCATE
-> ROOT CAUSE
-> REGRESSION TEST
-> MINIMAL FIX
-> AFFECTED CHECKS
-> VERIFY
```

Do not patch a guessed root cause. Search from the symptom/error toward the responsible symbol, then inspect direct dependencies, consumers and tests only as needed.

## Prompt

```text
@GitHub work with <owner>/<repo>.
Use cuongtobi/gpt-web-vibe-kit.

Fix:
<symptom>

Required:
reproduce/locate -> root cause -> regression test -> minimal fix -> affected checks -> verify.
```

For an urgent production issue, use mode `hotfix` and keep the same evidence-driven sequence with the smallest safe patch.
