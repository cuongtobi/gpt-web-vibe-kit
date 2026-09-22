# gpt-web-vibe-kit contributor instructions

This repository is the source kit for a GitHub-native vibe-coding workflow designed for ChatGPT Web.

## Principles
- Public workflow: session -> plan -> build -> verify -> github-review.
- GitHub is durable task state; previous chat history is never required.
- Stable project context belongs in versioned project files; per-task context belongs in the task PR body.
- Persist references to code (paths, symbols, blob SHAs, tests, consumers), not source copies.
- Keep model context bounded and fetch current code from GitHub.
- Static dependency evidence is advisory; current source, native tooling, tests and CI are authoritative.
- Never claim PASS_VERIFIED without current-head runtime/CI evidence.
- Runtime code in this kit remains Python-standard-library-only.

## Source of truth
1. Current target-repository source/configuration.
2. Current task PR body, branch, diff and CI.
3. Target project context under `.vibe/`.
4. This kit's skill contracts.
5. Chat history and assumptions.

## Development
When behavior changes, update tests and both README variants.

```bash
python -m unittest discover -s tests -v
python -m py_compile install.py runtime/state.py runtime/vibe_web.py
```
