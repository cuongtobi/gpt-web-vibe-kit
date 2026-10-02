# Rebase or base-branch change

When the base branch changes, do not assume the saved neighborhood is still valid.

Re-check targets, dependencies, consumers and tests. If the baseline changed materially, use `CONTEXT_REBUILD`; otherwise refresh only the bounded changed neighborhood.

After rebase or any new head, previous verification/security/frontend head-bound evidence is stale until verified again.
