# Feature or behavior change

Use `feature` for a new capability and `change` for an intentional change to existing behavior or compatibility.

## Flow

```text
desired behavior
-> public/config/data contracts
-> exact target
-> direct dependencies/consumers
-> focused tests
-> minimal implementation
-> current-head verification
```

Pay special attention to APIs, configuration, persisted data, serialized formats and backwards compatibility when they are in scope.

## Prompt

```text
@GitHub work with <owner>/<repo>.
Use cuongtobi/gpt-web-vibe-kit.

Task:
<feature or behavior change>

Requirements:
- preserve <contract>;
- add focused tests;
- do not add a dependency unless needed.

Run the full workflow.
```

Do not add speculative abstractions or unrelated cleanup.
