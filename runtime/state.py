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
}

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
    "controls", "evidence", "head_sha", "limitations",
}
FRONTEND_KEYS = {"surface", "intent", "design_context", "acceptance_dimensions", "visual_qa"}
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


def _require_string_list(value: Any, name: str) -> None:
    _require(isinstance(value, list), f"{name} must be a list")
    for item in value:
        _require_string(item, f"{name} item")


def _reject_unknown_keys(data: Mapping[str, Any], allowed: set[str], name: str) -> None:
    unknown = sorted(set(data) - allowed)
    _require(not unknown, f"{name} contains unknown fields: {', '.join(unknown)}")


def validate_vibe_config(data: Mapping[str, Any]) -> None:
    _require(isinstance(data, Mapping), "config must be an object")
    _require(data.get("version") in {1, 2}, "config version must be 1 or 2")
    context = data.get("context")
    _require(isinstance(context, Mapping), "config.context must be an object")
    for key in ("max_dependency_depth", "max_source_files", "max_test_files", "max_related_modules"):
        value = context.get(key, DEFAULT_CONTEXT_LIMITS[key])
        _require(isinstance(value, int) and value >= 0, f"config.context.{key} must be a non-negative integer")
    ratio = context.get("rebuild_changed_ratio", DEFAULT_CONTEXT_LIMITS["rebuild_changed_ratio"])
    _require(isinstance(ratio, (int, float)) and 0 <= ratio <= 1, "config.context.rebuild_changed_ratio must be between 0 and 1")
    verification = data.get("verification", {})
    _require(isinstance(verification, Mapping), "config.verification must be an object")
    _require_string_list(verification.get("commands", []), "config.verification.commands")


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
    _require_string_list(data.get("targets"), "targets")

    context = data.get("context")
    _require(isinstance(context, Mapping), "context must be an object")
    _reject_unknown_keys(context, CONTEXT_KEYS, "context")
    for key in ("symbols", "dependencies", "consumers", "tests", "config_files"):
        _require_string_list(context.get(key), f"context.{key}")

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
        _require_string_list(item.get("symbols"), "observed file symbols")
        _require(item["path"] not in observed_paths, f"duplicate observed file path: {item['path']}")
        observed_paths.add(item["path"])

    referenced_paths = set(data["targets"])
    for key in ("dependencies", "consumers", "tests", "config_files"):
        referenced_paths.update(context[key])
    missing = sorted(referenced_paths - observed_paths)
    _require(not missing, "referenced context files must appear in observed_files: " + ", ".join(missing))

    acceptance = data.get("acceptance")
    _require(isinstance(acceptance, list), "acceptance must be a list")
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
        for key in ("surfaces", "trust_boundaries", "abuse_cases", "controls", "limitations"):
            _require_string_list(security.get(key), f"security.{key}")
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
        _require(len(dimensions) == len(set(dimensions)), "frontend.acceptance_dimensions must be unique")
        for dimension in dimensions:
            _require(dimension in VALID_FRONTEND_DIMENSIONS, f"invalid frontend acceptance dimension: {dimension}")

        visual_qa = frontend.get("visual_qa")
        _require(isinstance(visual_qa, Mapping), "frontend.visual_qa must be an object")
        _reject_unknown_keys(visual_qa, VISUAL_QA_KEYS, "frontend.visual_qa")
        max_rounds = visual_qa.get("max_rounds")
        _require(
            isinstance(max_rounds, int) and not isinstance(max_rounds, bool) and 1 <= max_rounds <= 2,
            "frontend.visual_qa.max_rounds must be an integer between 1 and 2",
        )
        _require_string_list(visual_qa.get("browser_tooling"), "frontend.visual_qa.browser_tooling")
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


def validate_project_context(data: Mapping[str, Any]) -> None:
    _require(data.get("schema_version") == 1, "project context schema_version must be 1")
    _require(isinstance(data.get("project"), Mapping), "project must be an object")
    _require_string_list(data.get("languages", []), "languages")
    _require_string_list(data.get("frameworks", []), "frameworks")
    _require_string_list(data.get("entrypoints", []), "entrypoints")
    primary = data.get("primary_language")
    _require(primary is None or isinstance(primary, str), "primary_language must be a string or null")
    limits = data.get("context_limits")
    _require(isinstance(limits, Mapping), "context_limits must be an object")
    for key in ("max_dependency_depth", "max_source_files", "max_test_files", "max_related_modules"):
        value = limits.get(key)
        _require(isinstance(value, int) and value >= 0, f"context_limits.{key} must be a non-negative integer")
    verification = data.get("verification")
    _require(isinstance(verification, Mapping), "verification must be an object")
    _require_string_list(verification.get("commands", []), "verification.commands")
    dependency_authority = data.get("dependency_authority")
    _require(isinstance(dependency_authority, Mapping), "dependency_authority must be an object")


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
    return (
        verification["status"] == "PASS_VERIFIED"
        and verification["head_sha"] == manifest["head_sha"]
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
    if verification["head_sha"] != head_sha and verification["status"] == "PASS_VERIFIED":
        verification["status"] = None
        verification["ci_run_id"] = None
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
