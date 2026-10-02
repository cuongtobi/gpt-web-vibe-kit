# Security reference

The kit does **not** guarantee that generated or modified code is secure. Its enforceable workflow rule is:

> Security-sensitive changes cannot silently pass without explicit security review/evidence.

Treat work as security-sensitive when the request or discovered impact reaches trust boundaries such as authentication/authorization, sessions/tokens/passwords, upload/filesystem access, user-controlled database queries or URLs, HTML/template rendering, command execution, payments/webhooks, secrets/credentials or comparable surfaces.

## Manifest state

Security-sensitive tasks record:

- affected surfaces;
- trust boundaries;
- plausible abuse/failure cases;
- controls that must remain intact;
- structured security evidence;
- evidence `head_sha`;
- limitations.

Runtime candidate detection is conservative and advisory. If a candidate is reviewed but kept `standard`, `security.candidate_disposition` explains why.

Normal lint/test/build success alone is not sufficient security evidence for a security-sensitive task. Missing scanner/tooling must be reported as a limitation rather than silently treated as success.

Agent-level implementation and review rules live in the workflow skills.
