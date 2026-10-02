# Review an existing PR

Use the `github-review` skill against the current PR state.

## Check

- exactly one valid schema-v2 manifest;
- manifest head matches the current PR head;
- saved context fits the configured budget;
- diff matches accepted scope;
- direct consumers/contracts/tests are accounted for;
- frontend/security classification matches the final diff;
- current-head CI and required evidence are valid;
- unresolved review threads are handled.

## Prompt

```text
@GitHub review PR #<number> in <owner>/<repo>.
Use cuongtobi/gpt-web-vibe-kit.
Run github-review against the current head and report blockers.
```
