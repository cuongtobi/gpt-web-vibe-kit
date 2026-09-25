from __future__ import annotations

import json
from copy import deepcopy
from typing import Any, Mapping

TASK_START = "<!-- gpt-web-vibe:task:start -->"
TASK_END = "<!-- gpt-web-vibe:task:end -->"
TASK_SCHEMA_VERSION = 2

VALID_MODES = {"feature", "change", "bug_fix", "refactor", "hotfix", "test", "docs"}
VALID_STATUSES = {"planning", "building", "verifying", "blocked", "ready", "complete"}
VALID_ACCEPTANCE_STATUSES = {"pending", "met", "failed", "unverified"}
VALID_VERIFICATION_STATUSES = {None, "PASS_VERIFIED", "FAIL_VERIFICATION", "NEEDS_VERIFICATION_CONFIG"}
VALID_OBSERVED_ROLES = {"target", "dependency", "consumer", "test", "config", "related"}
VALID_SECURITY_CLASSIFICATIONS = {"standard", "security-sensitive"}
VALID_FRONTEND_SURFACES = {"marketing", "application", "content", "commerce", "admin", "component"}
VALID_FRONTEND_INTENTS = {"refine", "redesign"}
VALID_FRONTEND_DIMENSIONS = {
    "visual-consistency",
    "responsive-behavior",
    "interaction-states",
    "accessibility",
    "content-layout-integrity",
}
VALID_DESIGN_CONTEXT_MODES = {"declared", "infer-existing-ui"}

DEFAULT_CONTEXT_LIMITS = {
    "max_dependency_depth": 2,
    "max_source_files": 15,
    "max_test_files": 6,
    "max_related_modules": 6,
    "rebuild_changed_ratio": 0.5,
    "max_search_rounds": 3,
    "max_symbol_hints": 24,
}

CONFIG_V2_KEYS = {
    "version", "workflow", "manifest_schema_version", "kit_repository",
    "github", "context", "verification",
}
CONFIG_V1_KEYS = {"version", "context", "verification"}
CONFIG_GITHUB_KEYS = {"task_state", "branch_prefix"}
CONFIG_CONTEXT_KEYS = set(DEFAULT_CONTEXT_LIMITS)
CONFIG_VERIFICATION_KEYS = {"require_commands", "commands"}

TASK_KEYS = {
    "schema_version", "task_id", "mode", "status", "request",
    "base_branch", "base_sha", "head_branch", "head_sha",
    "targets", "context", "acceptance", "verification", "security", "frontend", "uncertainties",
}
CONTEXT_KEYS = {
    "symbols", "dependencies", "consumers", "tests", "config_files", "observed_files",
}
OBSERVED_FILE_KEYS = {"path", "sha", "role", "depth", "symbols"}
ACCEPTANCE_KEYS = {"id", "expected", "status", "evidence"}
EVIDENCE_KEYS = {"type", "ref"}
VERIFICATION_KEYS = {"commands", "head_sha", "ci_run_id", "status"}
SECURITY_KEYS = {
    "classification", "surfaces", "trust_boundaries", "abuse_cases",
    "controls", "evidence", "head_sha", "limitations", "candidate_disposition",
}
FRONTEND_KEYS = {
    "surface", "intent", "design_context", "acceptance_dimensions",
    "acceptance_map", "visual_qa",
}
DESIGN_CONTEXT_KEYS = {"path", "mode"}
VISUAL_QA_KEYS = {"max_rounds", "browser_tooling", "evidence", "head_sha", "limitations"}


class ManifestError(ValueError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ManifestError(message)


def _require_string(value: Any, name: str, *, allow_empty: bool = False) -> None:
    _require(isinstance(value, str), f"{name} must be a string")
    if not allow_empty:
        _require(bool(value.strip()), f"{name} is required")


def _require_string_list(value: Any, name: str, *, unique: bool = False) -> None:
    _require(isinstance(value, list), f"{name} must be a list")
    for item in value:
        _require_string(item, f"{name} item")
    if unique:
        _require(len(value) == len(set(value)), f"{name} must contain unique items")


def _reject_unknown_keys(data: Mapping[str, Any], allowed: set[str], name: str) -> None:
    unknown = sorted(set(data) - allowed)
    _require(not unknown, f"{name} contains unknown fields: {', '.join(unknown)}")


def validate_vibe_config(data: Mapping[str, Any]) -> None:
    _require(isinstance(data, Mapping), "config must be an object")
    version = data.get("version")
    _require(version in {1, 2}, "config version must be 1 or 2")
    _reject_unknown_keys(data, CONFIG_V2_KEYS if version == 2 else CONFIG_V1_KEYS, "config")

    if version == 2:
        _require(data.get("workflow") == "github-native", "config.workflow must be github-native")
        _require(
            data.get("manifest_schema_version") == TASK_SCHEMA_VERSION,
            f"config.manifest_schema_version must be {TASK_SCHEMA_VERSION}",
        )
        _require_string(data.get("kit_repository"), "config.kit_repository")
        github = data.get("github")
        _require(isinstance(github, Mapping), "config.github must be an object")
        _reject_unknown_keys(github, CONFIG_GITHUB_KEYS, "config.github")
        _require(github.get("task_state") == "pull_request_body", "config.github.task_state must be pull_request_body")
        _require_string(github.get("branch_prefix"), "config.github.branch_prefix")

    context = data.get("context")
    _require(isinstance(context, Mapping), "config.context must be an object")
    _reject_unknown_keys(context, CONFIG_CONTEXT_KEYS, "config.context")
    for key in (
        "max_dependency_depth", "max_source_files", "max_test_files",
        "max_related_modules", "max_search_rounds", "max_symbol_hints",
    ):
        value = context.get(key, DEFAULT_CONTEXT_LIMITS[key])
        minimum = 1 if key == "max_search_rounds" else 0
        _require(
            isinstance(value, int) and not isinstance(value, bool) and value >= minimum,
            f"config.context.{key} must be an integer >= {minimum}",
        )
    ratio = context.get("rebuild_changed_ratio", DEFAULT_CONTEXT_LIMITS["rebuild_changed_ratio"])
    _require(
        isinstance(ratio, (int, float)) and not isinstance(ratio, bool) and 0 <= ratio <= 1,
        "config.context.rebuild_changed_ratio must be between 0 and 1",
    )

    verification = data.get("verification", {})
    _require(isinstance(verification, Mapping), "config.verification must be an object")
    _reject_unknown_keys(verification, CONFIG_VERIFICATION_KEYS, "config.verification")
    require_commands = verification.get("require_commands", True)
    _require(isinstance(require_commands, bool), "config.verification.require_commands must be a boolean")
    _require_string_list(verification.get("commands", []), "config.verification.commands", unique=True)


def context_limits(config: Mapping[str, Any] | None = None) -> dict[str, Any]:
    result = dict(DEFAULT_CONTEXT_LIMITS)
    if config is None:
        return result
    validate_vibe_config(config)
    result.update(config.get("context", {}))
    return result


def validate_task_manifest(data: Mapping[str, Any]) -> None:
    _require(isinstance(data, Mapping), "task manifest must be an object")
    _reject_unknown_keys(data, TASK_KEYS, "task manifest")
    _require(data.get("schema_version") == TASK_SCHEMA_VERSION, f"task schema_version must be {TASK_SCHEMA_VERSION}")
    _require_string(data.get("task_id"), "task_id")
    _require(data.get("mode") in VALID_MODES, "invalid task mode")
    _require(data.get("status") in VALID_STATUSES, "invalid task status")
    _require_string(data.get("request"), "request")
    for key in ("base_branch", "base_sha", "head_branch", "head_sha"):
        _require_string(data.get(key), key)
    _require_string_list(data.get("targets"), "targets", unique=True)

    context = data.get("context")
    _require(isinstance(context, Mapping), "context must be an object")
    _reject_unknown_keys(context, CONTEXT_KEYS, "context")
    for key in ("symbols", "dependencies", "consumers", "tests", "config_files"):
        _require_string_list(context.get(key), f"context.{key}", unique=True)

    observed = context.get("observed_files")
    _require(isinstance(observed, list), "context.observed_files must be a list")
    observed_paths: set[str] = set()
    for item in observed:
        _require(isinstance(item, Mapping), "observed file entries must be objects")
        _reject_unknown_keys(item, OBSERVED_FILE_KEYS, "observed file")
        _require_string(item.get("path"), "observed file path")
        _require_string(item.get("sha"), "observed file sha")
        _require(item.get("role") in VALID_OBSERVED_ROLES, "invalid observed file role")
        _require(isinstance(item.get("depth"), int) and item["depth"] >= 0, "observed file depth must be a non-negative integer")
        _require_string_list(item.get("symbols"), "observed file symbols", unique=True)
        _require(item["path"] not in observed_paths, f"duplicate observed file path: {item['path']}")
        observed_paths.add(item["path"])

    referenced_paths = set(data["targets"])
    for key in ("dependencies", "consumers", "tests", "config_files"):
        referenced_paths.update(context[key])
    missing = sorted(referenced_paths - observed_paths)
    _require(not missing, "referenced context files must appear in observed_files: " + ", ".join(missing))

    acceptance = data.get("acceptance")
    _require(
        isinstance(acceptance, list) and bool(acceptance),
        "acceptance must be a non-empty list",
    )
    ids: set[str] = set()
    for item in acceptance:
        _require(isinstance(item, Mapping), "acceptance entries must be objects")
        _reject_unknown_keys(item, ACCEPTANCE_KEYS, "acceptance entry")
        criterion_id = item.get("id")
        _require_string(criterion_id, "acceptance id")
        _require(criterion_id not in ids, "acceptance ids must be unique")
        ids.add(criterion_id)
        _require_string(item.get("expected"), f"acceptance {criterion_id} expected")
        _require(item.get("status") in VALID_ACCEPTANCE_STATUSES, f"invalid acceptance status for {criterion_id}")
        evidence = item.get("evidence")
        _require(isinstance(evidence, list), f"acceptance {criterion_id} evidence must be a list")
        for ev in evidence:
            _require(isinstance(ev, Mapping), "acceptance evidence entries must be objects")
            _reject_unknown_keys(ev, EVIDENCE_KEYS, "acceptance evidence")
            _require_string(ev.get("type"), "acceptance evidence type")
            _require_string(ev.get("ref"), "acceptance evidence ref")

    verification = data.get("verification")
    _require(isinstance(verification, Mapping), "verification must be an object")
    _reject_unknown_keys(verification, VERIFICATION_KEYS, "verification")
    _require_string_list(verification.get("commands"), "verification.commands")
    verification_head = verification.get("head_sha")
    _require(verification_head is None or (isinstance(verification_head, str) and bool(verification_head.strip())),
             "verification.head_sha must be null or a non-empty string")
    ci_run_id = verification.get("ci_run_id")
    _require(ci_run_id is None or (isinstance(ci_run_id, int) and ci_run_id > 0),
             "verification.ci_run_id must be null or a positive integer")
    verification_status = verification.get("status")
    _require(verification_status in VALID_VERIFICATION_STATUSES, "invalid verification status")
    if verification_status == "PASS_VERIFIED":
        _require(verification_head == data["head_sha"], "PASS_VERIFIED evidence must belong to current head_sha")

    security = data.get("security")
    if security is not None:
        _require(isinstance(security, Mapping), "security must be an object")
        _reject_unknown_keys(security, SECURITY_KEYS, "security")
        classification = security.get("classification")
        _require(classification in VALID_SECURITY_CLASSIFICATIONS, "invalid security classification")
        for key in ("surfaces", "trust_boundaries", "abuse_cases", "controls"):
            _require_string_list(security.get(key), f"security.{key}", unique=True)
        _require_string_list(security.get("limitations"), "security.limitations")
        candidate_disposition = security.get("candidate_disposition")
        _require(
            candidate_disposition is None
            or (isinstance(candidate_disposition, str) and bool(candidate_disposition.strip())),
            "security.candidate_disposition must be null or a non-empty string",
        )
        evidence = security.get("evidence")
        _require(isinstance(evidence, list), "security.evidence must be a list")
        for ev in evidence:
            _require(isinstance(ev, Mapping), "security evidence entries must be objects")
            _reject_unknown_keys(ev, EVIDENCE_KEYS, "security evidence")
            _require_string(ev.get("type"), "security evidence type")
            _require_string(ev.get("ref"), "security evidence ref")
        security_head = security.get("head_sha")
        _require(
            security_head is None or (isinstance(security_head, str) and bool(security_head.strip())),
            "security.head_sha must be null or a non-empty string",
        )
        if classification == "security-sensitive":
            _require(bool(security.get("surfaces")), "security-sensitive tasks must identify at least one surface")
            if verification_status == "PASS_VERIFIED":
                _require(security_head == data["head_sha"], "security evidence must belong to current head_sha")
                _require(bool(evidence), "security-sensitive PASS_VERIFIED requires security evidence")

    frontend = data.get("frontend")
    if frontend is not None:
        _require(isinstance(frontend, Mapping), "frontend must be an object")
        _reject_unknown_keys(frontend, FRONTEND_KEYS, "frontend")
        _require(frontend.get("surface") in VALID_FRONTEND_SURFACES, "invalid frontend surface")
        _require(frontend.get("intent") in VALID_FRONTEND_INTENTS, "invalid frontend intent")

        design_context = frontend.get("design_context")
        _require(isinstance(design_context, Mapping), "frontend.design_context must be an object")
        _reject_unknown_keys(design_context, DESIGN_CONTEXT_KEYS, "frontend.design_context")
        design_path = design_context.get("path")
        _require(
            design_path is None or (isinstance(design_path, str) and bool(design_path.strip())),
            "frontend.design_context.path must be null or a non-empty string",
        )
        _require(
            design_context.get("mode") in VALID_DESIGN_CONTEXT_MODES,
            "invalid frontend design-context mode",
        )

        dimensions = frontend.get("acceptance_dimensions")
        _require(isinstance(dimensions, list) and bool(dimensions), "frontend.acceptance_dimensions must be a non-empty list")
        for dimension in dimensions:
            _require(isinstance(dimension, str), "frontend acceptance dimensions must be strings")
            _require(dimension in VALID_FRONTEND_DIMENSIONS, f"invalid frontend acceptance dimension: {dimension}")
        _require(len(dimensions) == len(set(dimensions)), "frontend.acceptance_dimensions must be unique")

        acceptance_map = frontend.get("acceptance_map")
        if acceptance_map is not None:
            _require(isinstance(acceptance_map, Mapping), "frontend.acceptance_map must be an object")
            for dimension, criterion_ids in acceptance_map.items():
                _require(dimension in dimensions, f"frontend.acceptance_map has undeclared dimension: {dimension}")
                _require_string_list(
                    criterion_ids,
                    f"frontend.acceptance_map.{dimension}",
                    unique=True,
                )
                _require(bool(criterion_ids), f"frontend.acceptance_map.{dimension} must not be empty")
                for criterion_id in criterion_ids:
                    _require(
                        criterion_id in ids,
                        f"frontend.acceptance_map.{dimension} references unknown acceptance id: {criterion_id}",
                    )

        visual_qa = frontend.get("visual_qa")
        _require(isinstance(visual_qa, Mapping), "frontend.visual_qa must be an object")
        _reject_unknown_keys(visual_qa, VISUAL_QA_KEYS, "frontend.visual_qa")
        max_rounds = visual_qa.get("max_rounds")
        _require(
            isinstance(max_rounds, int) and not isinstance(max_rounds, bool) and 1 <= max_rounds <= 2,
            "frontend.visual_qa.max_rounds must be an integer between 1 and 2",
        )
        browser_tooling = visual_qa.get("browser_tooling")
        _require_string_list(browser_tooling, "frontend.visual_qa.browser_tooling")
        _require(len(browser_tooling) == len(set(browser_tooling)), "frontend.visual_qa.browser_tooling must be unique")
        frontend_evidence = visual_qa.get("evidence")
        _require(isinstance(frontend_evidence, list), "frontend.visual_qa.evidence must be a list")
        for ev in frontend_evidence:
            _require(isinstance(ev, Mapping), "frontend visual evidence entries must be objects")
            _reject_unknown_keys(ev, EVIDENCE_KEYS, "frontend visual evidence")
            _require_string(ev.get("type"), "frontend visual evidence type")
            _require_string(ev.get("ref"), "frontend visual evidence ref")
        frontend_head = visual_qa.get("head_sha")
        _require(
            frontend_head is None or (isinstance(frontend_head, str) and bool(frontend_head.strip())),
            "frontend.visual_qa.head_sha must be null or a non-empty string",
        )
        _require_string_list(visual_qa.get("limitations"), "frontend.visual_qa.limitations")
        if frontend_evidence:
            _require(
                frontend_head == data["head_sha"],
                "frontend visual evidence must belong to current head_sha",
            )

    _require_string_list(data.get("uncertainties"), "uncertainties")

    if verification_status == "PASS_VERIFIED":
        for item in acceptance:
            _require(
                item["status"] == "met",
                f"PASS_VERIFIED requires acceptance {item['id']} to be met",
            )
            _require(
                bool(item["evidence"]),
                f"PASS_VERIFIED requires evidence for acceptance {item['id']}",
            )
        violations = _completion_violations_no_validate(
            data,
            None,
            check_commands=False,
        )
        _require(
            not violations,
            "PASS_VERIFIED violates completion gate: " + "; ".join(violations),
        )

    if data.get("status") in {"ready", "complete"}:
        _require(
            verification_status == "PASS_VERIFIED",
            f"task status {data['status']} requires PASS_VERIFIED",
        )


def validate_project_context(data: Mapping[str, Any]) -> None:
    _require(isinstance(data, Mapping), "project context must be an object")
    allowed = {
        "schema_version", "project", "languages", "primary_language", "frameworks",
        "entrypoints", "verification", "context_limits", "dependency_authority",
    }
    _reject_unknown_keys(data, allowed, "project context")
    _require(data.get("schema_version") == 1, "project context schema_version must be 1")

    project = data.get("project")
    _require(isinstance(project, Mapping), "project must be an object")
    _reject_unknown_keys(project, {"name", "summary"}, "project")
    for key in ("name", "summary"):
        value = project.get(key)
        _require(value is None or isinstance(value, str), f"project.{key} must be a string or null")

    _require_string_list(data.get("languages", []), "languages", unique=True)
    _require_string_list(data.get("frameworks", []), "frameworks", unique=True)
    _require_string_list(data.get("entrypoints", []), "entrypoints", unique=True)
    primary = data.get("primary_language")
    _require(primary is None or isinstance(primary, str), "primary_language must be a string or null")
    if primary is not None:
        _require(primary in data.get("languages", []), "primary_language must be present in languages")

    limits = data.get("context_limits")
    _require(isinstance(limits, Mapping), "context_limits must be an object")
    limit_keys = {"max_dependency_depth", "max_source_files", "max_test_files", "max_related_modules"}
    _reject_unknown_keys(limits, limit_keys, "context_limits")
    for key in limit_keys:
        value = limits.get(key)
        _require(
            isinstance(value, int) and not isinstance(value, bool) and value >= 0,
            f"context_limits.{key} must be a non-negative integer",
        )

    verification = data.get("verification")
    _require(isinstance(verification, Mapping), "verification must be an object")
    _reject_unknown_keys(verification, {"commands"}, "verification")
    _require_string_list(verification.get("commands", []), "verification.commands", unique=True)

    dependency_authority = data.get("dependency_authority")
    _require(isinstance(dependency_authority, Mapping), "dependency_authority must be an object")
    _reject_unknown_keys(dependency_authority, {"level", "model"}, "dependency_authority")
    _require_string(dependency_authority.get("level"), "dependency_authority.level")
    _require_string(dependency_authority.get("model"), "dependency_authority.model")


def extract_task_manifest(body: str) -> dict[str, Any]:
    start_count = body.count(TASK_START)
    end_count = body.count(TASK_END)
    if start_count != 1 or end_count != 1:
        raise ManifestError(
            f"task manifest block must appear exactly once (start={start_count}, end={end_count})"
        )
    start = body.find(TASK_START)
    end = body.find(TASK_END)
    if end <= start:
        raise ManifestError("task manifest end marker must follow start marker")
    raw = body[start + len(TASK_START):end].strip()
    if raw.startswith("```json"):
        raw = raw[len("```json"):].strip()
    elif raw.startswith("```"):
        raw = raw[len("```"):].strip()
    if raw.endswith("```"):
        raw = raw[:-3].strip()
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ManifestError(f"invalid task manifest JSON: {exc}") from exc
    _require(isinstance(data, dict), "task manifest must be an object")
    validate_task_manifest(data)
    return data


def render_task_manifest(body: str, manifest: Mapping[str, Any]) -> str:
    validate_task_manifest(manifest)
    start_count = body.count(TASK_START)
    end_count = body.count(TASK_END)
    if start_count != end_count or start_count > 1:
        raise ManifestError(
            f"cannot render into body with duplicate/mismatched task markers (start={start_count}, end={end_count})"
        )
    block = (
        f"{TASK_START}\n```json\n"
        + json.dumps(manifest, indent=2, sort_keys=True)
        + f"\n```\n{TASK_END}"
    )
    if start_count == 1:
        start = body.find(TASK_START)
        end = body.find(TASK_END, start)
        if end <= start:
            raise ManifestError("task manifest end marker must follow start marker")
        end += len(TASK_END)
        return body[:start].rstrip() + "\n\n" + block + body[end:]
    prefix = body.rstrip()
    return (prefix + "\n\n" if prefix else "") + block + "\n"


def context_budget_violations(
    manifest: Mapping[str, Any],
    config: Mapping[str, Any] | None = None,
) -> list[str]:
    validate_task_manifest(manifest)
    limits = context_limits(config)
    observed = manifest["context"]["observed_files"]

    source_paths = {
        item["path"] for item in observed
        if item["role"] in {"target", "dependency", "consumer", "config", "related"}
    }
    test_paths = {item["path"] for item in observed if item["role"] == "test"}
    related_paths = {
        item["path"] for item in observed
        if item["role"] in {"dependency", "consumer", "related"}
    }
    max_depth = max((item["depth"] for item in observed), default=0)

    violations: list[str] = []
    if len(source_paths) > limits["max_source_files"]:
        violations.append(
            f"source files {len(source_paths)} exceed max_source_files={limits['max_source_files']}"
        )
    if len(test_paths) > limits["max_test_files"]:
        violations.append(
            f"test files {len(test_paths)} exceed max_test_files={limits['max_test_files']}"
        )
    if len(related_paths) > limits["max_related_modules"]:
        violations.append(
            f"related modules {len(related_paths)} exceed max_related_modules={limits['max_related_modules']}"
        )
    if max_depth > limits["max_dependency_depth"]:
        violations.append(
            f"dependency depth {max_depth} exceeds max_dependency_depth={limits['max_dependency_depth']}"
        )
    return violations


def context_decision(
    manifest: Mapping[str, Any],
    current_shas: Mapping[str, str],
    *,
    config: Mapping[str, Any] | None = None,
    scope_changed: bool = False,
    base_changed_materially: bool = False,
) -> dict[str, Any]:
    validate_task_manifest(manifest)
    violations = context_budget_violations(manifest, config)
    if violations:
        return {
            "state": "CONTEXT_REBUILD",
            "changed_files": [],
            "reason": "context-budget-exceeded",
            "violations": violations,
        }
    if scope_changed:
        return {"state": "CONTEXT_REBUILD", "changed_files": [], "reason": "task-scope-changed"}
    if base_changed_materially:
        return {"state": "CONTEXT_REBUILD", "changed_files": [], "reason": "base-changed-materially"}

    observed = manifest["context"]["observed_files"]
    if not observed:
        return {"state": "CONTEXT_REBUILD", "changed_files": [], "reason": "no-observed-files"}

    changed = [item["path"] for item in observed if current_shas.get(item["path"]) != item["sha"]]
    if not changed:
        return {"state": "CONTEXT_HIT", "changed_files": [], "reason": "observed-files-unchanged"}

    limits = context_limits(config)
    ratio = len(changed) / len(observed)
    if ratio > limits["rebuild_changed_ratio"]:
        return {
            "state": "CONTEXT_REBUILD",
            "changed_files": sorted(changed),
            "reason": "too-many-observed-files-changed",
        }
    return {
        "state": "CONTEXT_REFRESH",
        "changed_files": sorted(changed),
        "reason": "bounded-file-delta",
    }


SECURITY_CANDIDATE_TERMS = {
    "authentication": ("auth", "authentication", "login", "sign-in", "signin", "credential"),
    "authorization": ("authorization", "permission", "role", "access control", "acl"),
    "session-token-password": (
        "session", "token", "jwt", "cookie", "password", "refresh_token",
        "refresh-token", "api key", "apikey",
    ),
    "upload-filesystem": ("upload", "filesystem", "file path", "path traversal", "attachment"),
    "database-query": ("sql", "query", "database", "db"),
    "user-controlled-url": ("webhook", "callback url", "redirect url", "fetch url", "http client"),
    "html-template": ("html", "template", "render", "xss"),
    "command-execution": ("command", "shell", "subprocess", "exec", "spawn"),
    "payment-webhook": ("payment", "checkout", "billing", "webhook"),
    "secrets-credentials": ("secret", "credential", "private key", "access key"),
}

FRONTEND_VISUAL_DIMENSIONS = {
    "visual-consistency",
    "responsive-behavior",
    "content-layout-integrity",
}


def _normalized_security_text(value: str) -> str:
    normalized = value.lower()
    for separator in ("_", "-", "/", "\\", ".", ":"):
        normalized = normalized.replace(separator, " ")
    return " " + " ".join(normalized.split()) + " "


def security_candidate_surfaces(manifest: Mapping[str, Any]) -> list[str]:
    context = manifest.get("context") if isinstance(manifest.get("context"), Mapping) else {}
    observed = context.get("observed_files", []) if isinstance(context, Mapping) else []
    parts = [
        str(manifest.get("request", "")),
        *[str(item) for item in manifest.get("targets", []) if isinstance(item, str)],
        *[str(item) for item in context.get("symbols", []) if isinstance(item, str)],
        *[
            str(item.get("path", ""))
            for item in observed
            if isinstance(item, Mapping)
        ],
    ]
    text = _normalized_security_text(" ".join(parts))
    return [
        surface
        for surface, terms in SECURITY_CANDIDATE_TERMS.items()
        if any(_normalized_security_text(term) in text for term in terms)
    ]


def _config_requires_commands(config: Mapping[str, Any] | None) -> bool:
    if config is None:
        return True
    validate_vibe_config(config)
    return bool(config.get("verification", {}).get("require_commands", True))


def _completion_violations_no_validate(
    manifest: Mapping[str, Any],
    config: Mapping[str, Any] | None,
    *,
    check_commands: bool = True,
) -> list[str]:
    violations: list[str] = []
    verification = manifest.get("verification", {})
    acceptance = manifest.get("acceptance", [])

    for item in acceptance:
        criterion_id = item.get("id", "<unknown>")
        if item.get("status") != "met":
            violations.append(f"acceptance {criterion_id} is not met")
        elif not item.get("evidence"):
            violations.append(f"acceptance {criterion_id} has no evidence")

    if verification.get("status") != "PASS_VERIFIED":
        violations.append("verification status is not PASS_VERIFIED")
    if verification.get("head_sha") != manifest.get("head_sha"):
        violations.append("verification evidence is not bound to current head")
    if check_commands and _config_requires_commands(config) and not verification.get("commands"):
        violations.append("verification commands are required but empty")

    security = manifest.get("security")
    candidates = security_candidate_surfaces(manifest)
    if candidates:
        if not isinstance(security, Mapping):
            violations.append(
                "security candidate surfaces require explicit security classification: "
                + ", ".join(candidates)
            )
        elif security.get("classification") == "standard" and not security.get("candidate_disposition"):
            violations.append(
                "standard classification for security candidates requires candidate_disposition: "
                + ", ".join(candidates)
            )

    if isinstance(security, Mapping) and security.get("classification") == "security-sensitive":
        if security.get("head_sha") != manifest.get("head_sha") or not security.get("evidence"):
            violations.append("security-sensitive task lacks current-head security evidence")

    frontend = manifest.get("frontend")
    if isinstance(frontend, Mapping):
        acceptance_by_id = {
            item.get("id"): item
            for item in acceptance
            if isinstance(item, Mapping)
        }
        dimensions = frontend.get("acceptance_dimensions", [])
        acceptance_map = frontend.get("acceptance_map")
        if not isinstance(acceptance_map, Mapping):
            violations.append("frontend acceptance dimensions are not bound to acceptance criteria")
        else:
            for dimension in dimensions:
                criterion_ids = acceptance_map.get(dimension, [])
                if not criterion_ids:
                    violations.append(f"frontend dimension {dimension} has no acceptance mapping")
                    continue
                for criterion_id in criterion_ids:
                    item = acceptance_by_id.get(criterion_id)
                    if not item or item.get("status") != "met" or not item.get("evidence"):
                        violations.append(
                            f"frontend dimension {dimension} lacks met evidence through {criterion_id}"
                        )
        visual_qa = frontend.get("visual_qa", {})
        if any(dimension in FRONTEND_VISUAL_DIMENSIONS for dimension in dimensions):
            if not visual_qa.get("evidence") and not visual_qa.get("limitations"):
                violations.append(
                    "visual frontend dimensions require visual evidence or an explicit limitation"
                )
        if visual_qa.get("evidence") and visual_qa.get("head_sha") != manifest.get("head_sha"):
            violations.append("frontend visual evidence is not bound to current head")

    return violations


def completion_violations(
    manifest: Mapping[str, Any],
    config: Mapping[str, Any] | None = None,
) -> list[str]:
    validate_task_manifest(manifest)
    return _completion_violations_no_validate(manifest, config)


def task_ready_for_completion(
    manifest: Mapping[str, Any],
    config: Mapping[str, Any] | None = None,
) -> bool:
    return not completion_violations(manifest, config)


def verification_is_current(manifest: Mapping[str, Any]) -> bool:
    validate_task_manifest(manifest)
    verification = manifest["verification"]
    security = manifest.get("security")
    security_current = True
    if isinstance(security, Mapping) and security.get("classification") == "security-sensitive":
        security_current = (
            security.get("head_sha") == manifest["head_sha"]
            and bool(security.get("evidence"))
        )
    frontend = manifest.get("frontend")
    frontend_current = True
    if isinstance(frontend, Mapping):
        visual_qa = frontend.get("visual_qa")
        if isinstance(visual_qa, Mapping) and visual_qa.get("evidence"):
            frontend_current = visual_qa.get("head_sha") == manifest["head_sha"]
    acceptance_current = all(
        item.get("status") == "met" and bool(item.get("evidence"))
        for item in manifest.get("acceptance", [])
    )
    return (
        verification["status"] == "PASS_VERIFIED"
        and verification["head_sha"] == manifest["head_sha"]
        and acceptance_current
        and security_current
        and frontend_current
    )


def update_observed_shas(
    manifest: Mapping[str, Any],
    current_shas: Mapping[str, str],
) -> dict[str, Any]:
    result = deepcopy(dict(manifest))
    for item in result["context"]["observed_files"]:
        if item["path"] in current_shas:
            item["sha"] = current_shas[item["path"]]
    validate_task_manifest(result)
    return result


def update_manifest_head(manifest: Mapping[str, Any], head_sha: str) -> dict[str, Any]:
    _require_string(head_sha, "head_sha")
    result = deepcopy(dict(manifest))
    result["head_sha"] = head_sha
    verification = result["verification"]
    if verification["head_sha"] != head_sha:
        verification["head_sha"] = None
        verification["status"] = None
        verification["ci_run_id"] = None
        if result.get("status") in {"ready", "complete"}:
            result["status"] = "verifying"
    security = result.get("security")
    if isinstance(security, Mapping) and security.get("head_sha") != head_sha:
        security["head_sha"] = None
        security["evidence"] = []
    frontend = result.get("frontend")
    if isinstance(frontend, Mapping):
        visual_qa = frontend.get("visual_qa")
        if isinstance(visual_qa, Mapping) and visual_qa.get("head_sha") != head_sha:
            visual_qa["head_sha"] = None
            visual_qa["evidence"] = []
    validate_task_manifest(result)
    return result
