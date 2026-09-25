# Lightweight frontend policy

Use this reference only when the request or affected targets are genuinely user-interface work. A frontend-capable framework by itself does not make every task a frontend task: for example, a Next.js API/authentication refactor remains backend work unless the request or target evidence reaches the UI.

This policy augments the existing `session -> plan -> build -> verify -> github-review` flow. It does not create a new command, skill, manifest version, browser engine, or design runtime.

## Persisted frontend state

Frontend tasks may add the optional schema-v2 manifest block:

```json
{
  "frontend": {
    "surface": "application",
    "intent": "refine",
    "design_context": {
      "path": "DESIGN.md",
      "mode": "declared"
    },
    "acceptance_dimensions": [
      "visual-consistency",
      "responsive-behavior",
      "accessibility"
    ],
    "visual_qa": {
      "max_rounds": 2,
      "browser_tooling": ["playwright"],
      "evidence": [],
      "head_sha": null,
      "limitations": []
    }
  }
}
```

The block is optional. Backend/non-UI tasks should omit it rather than carrying empty frontend ceremony.

## Classification

Treat the task as frontend when the request or targets show concrete UI evidence such as:

- JSX/TSX/Vue/Svelte/Astro components or pages;
- HTML/CSS/Sass/Less styles/templates;
- component/layout/navigation/form/theme/responsive work;
- an explicit UI/UX/page/screen redesign.

Do not classify a task as frontend from a framework name alone or from generic words such as "design" or "redesign" when the affected target is architecture, API, database, authentication, tooling, or another non-UI surface.

## Preserve versus redesign

- `refine`: preserve the existing visual language, product behavior, copy, information architecture, interaction model, and unrelated UI. A spacing/responsive/component fix is not permission to redesign the product.
- `redesign`: visual language may change inside the accepted scope, but preserve product behavior, content truth, navigation/user flow, data contracts, and accessibility expectations unless the request explicitly changes them.
- Never invent marketing claims, fake data, or product behavior merely to make a screen look complete.

## Design context

- `DESIGN.md` is optional. If it exists and is relevant, read it and record it in the bounded observed context.
- If absent, use `design_context.mode: "infer-existing-ui"` and infer the incumbent system from bounded current files: tokens/theme configuration, CSS variables, shared UI components, fonts, spacing, layout primitives, icons, and nearby screens.
- Do not create `DESIGN.md` just because it is missing.
- Repository conventions win over generic aesthetic preferences unless the task explicitly requests a redesign.

## Surface priorities

Use one lightweight surface hint:

- `marketing`: hierarchy, identity, clarity, and action.
- `application`: task completion, scanability, consistency, and state clarity.
- `content`: readability, typography, navigation, and long-form rhythm.
- `commerce`: product/price/action clarity, trust, and error/empty/loading states.
- `admin`: information density, predictable controls, and efficient scanning.
- `component`: local consistency and reusable behavior without changing unrelated screens.

## Frontend quality floor

When relevant to the accepted change:

- Reuse existing components, tokens, icons, and interaction patterns before creating parallel ones.
- Keep semantic HTML and accessible names/labels; preserve keyboard and focus behavior.
- Cover loading, error, empty, disabled, hover, focus, and selected states only when the interaction can actually enter them.
- Treat responsive/mobile behavior as part of implementation rather than a later rewrite.
- Avoid accidental horizontal overflow, clipping, broken long content, or assumptions that only work with demo copy.
- Avoid unnecessary wrappers, card-in-card composition, decorative gradients/effects, or motion without a product/design reason.
- Keep non-trivial business behavior out of presentational components when the repository already has a suitable boundary.
- Do not add a frontend dependency when existing project capabilities can satisfy the task.

## Acceptance dimensions

Use only dimensions that materially apply:

1. `visual-consistency`
2. `responsive-behavior`
3. `interaction-states`
4. `accessibility`
5. `content-layout-integrity`

These dimensions become ordinary manifest acceptance criteria/evidence. Persist `frontend.acceptance_map` so every declared dimension names one or more ordinary acceptance IDs. A dimension is complete only through those mapped criteria; they are not five mandatory new tests.

## Visual verification

- Prefer browser/E2E/story/screenshot tooling already established in the target repository.
- Do not install Playwright, Cypress, a browser extension, or another visual runtime solely because this policy is active.
- Keep the same change to at most one primary visual inspection round plus one confirmation round. Batch findings before editing instead of entering an open-ended polish loop.
- When visual/browser verification is unavailable, record that in `frontend.visual_qa.limitations` and use the strongest available static/runtime evidence. For visual dimensions, either current visual evidence or an explicit limitation is required. Never claim visual behavior was verified when it was not.
- When visual evidence is recorded, bind `frontend.visual_qa.head_sha` to the current PR head. A new head invalidates the saved visual evidence.
