# Merge

The kit does not merge by default.

Merge only when:

- the task is ready on the current PR head;
- required acceptance evidence exists;
- verification is current;
- required frontend/security evidence is current;
- no unresolved blocker remains;
- the user or repository rules explicitly authorize merge.

## Prompt

```text
@GitHub check PR #<number>.
If the current head is ready with no blockers, squash merge it into main.
```
