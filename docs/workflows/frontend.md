# Frontend/UI work

Frontend work uses the normal task workflow; there is no separate design workflow.

Classify the task as frontend only when the request or affected target actually reaches UI code. A frontend-capable framework alone is not enough.

## Intent

- `refine`: preserve the incumbent visual language and unrelated product behavior.
- `redesign`: visual language may change inside the explicitly accepted scope.

Use existing tokens, shared components, interaction patterns and browser/E2E/screenshot tooling when available. Do not install visual tooling solely because the frontend policy applies.

Relevant acceptance dimensions may include visual consistency, responsive behavior, interaction states, accessibility and content/layout integrity. Declare only dimensions that materially apply.

## Prompt

```text
@GitHub work with <owner>/<repo>.
Use cuongtobi/gpt-web-vibe-kit.

Task:
<UI change>

Preserve existing behavior and visual language unless redesign is explicitly requested.
Use existing project tooling for verification.
```

See `skills/vibe/reference/frontend-policy.md` for the agent-level policy.
