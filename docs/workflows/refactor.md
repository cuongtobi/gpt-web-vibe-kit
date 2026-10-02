# Refactor

Mode: `refactor`.

Use this when structure changes but accepted behavior and public contracts should remain stable.

## Flow

```text
BASELINE
-> TARGET
-> DIRECT DEPENDENCIES
-> DIRECT CONSUMERS
-> TESTS / CONTRACTS
-> REFACTOR
-> OLD-REFERENCE SEARCH
-> VERIFY
```

Large refactors should be split into bounded PRs rather than bypassing the context budget.

## Prompt

```text
@GitHub work with <owner>/<repo>.
Use cuongtobi/gpt-web-vibe-kit.

Refactor <target>.
Preserve behavior and public contracts.

Before editing:
- find direct dependencies and consumers;
- capture baseline behavior/tests.

After editing:
- search old references;
- run affected checks;
- verify the current head.
```
