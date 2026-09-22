from __future__ import annotations

import json
from copy import deepcopy
from typing import Any, Mapping

TASK_START = "<!-- gpt-web-vibe:task:start -->"
TASK_END = "<!-- gpt-web-vibe:task:end -->"
VALID_MODES = {"feature", "change", "bug_fix", "refactor", "hotfix"}
VALID_STATUSES = {"planning", "building", "verifying", "blocked", "ready", "complete"}


class ManifestError(ValueError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ManifestError(message)


def validate_task_manifest(data: Mapping[str, Any]) -> None:
    _require(data.get("schema_version") == 1, "task schema_version must be 1")
    _require(isinstance(data.get("task_id"), str) and bool(data["task_id"].strip()), "task_id is required")
    _require(data.get("mode") in VALID_MODES, "invalid task mode")
    _require(data.get("status") in VALID_STATUSES, "invalid task status")
    _require(isinstance(data.get("request"), str) and bool(data["request"].strip()), "request is required")
    _require(isinstance(data.get("targets", []), list), "targets must be a list")
    context = data.get("context")
    _require(isinstance(context, Mapping), "context must be an object")
    for key in ("dependencies", "consumers", "tests", "config_files", "observed_files"):
        _require(isinstance(context.get(key, []), list), f"context.{key} must be a list")
    for item in context.get("observed_files", []):
        _require(isinstance(item, Mapping), "observed file entries must be objects")
        _require(isinstance(item.get("path"), str) and bool(item["path"]), "observed file path is required")
        _require(isinstance(item.get("sha"), str) and bool(item["sha"]), "observed file sha is required")
    acceptance = data.get("acceptance", [])
    _require(isinstance(acceptance, list), "acceptance must be a list")
    ids: set[str] = set()
    for item in acceptance:
        _require(isinstance(item, Mapping), "acceptance entries must be objects")
        criterion_id = item.get("id")
        _require(isinstance(criterion_id, str) and bool(criterion_id), "acceptance id is required")
        _require(criterion_id not in ids, "acceptance ids must be unique")
        ids.add(criterion_id)


def validate_project_context(data: Mapping[str, Any]) -> None:
    _require(data.get("schema_version") == 1, "project context schema_version must be 1")
    _require(isinstance(data.get("project"), Mapping), "project must be an object")
    _require(isinstance(data.get("languages", []), list), "languages must be a list")
    _require(isinstance(data.get("frameworks", []), list), "frameworks must be a list")
    _require(isinstance(data.get("context_limits"), Mapping), "context_limits must be an object")
    _require(isinstance(data.get("verification"), Mapping), "verification must be an object")


def extract_task_manifest(body: str) -> dict[str, Any]:
    start = body.find(TASK_START)
    end = body.find(TASK_END)
    if start < 0 or end < 0 or end <= start:
        raise ManifestError("task manifest block not found")
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
    block = (
        f"{TASK_START}\n```json\n"
        + json.dumps(manifest, indent=2, sort_keys=True)
        + f"\n```\n{TASK_END}"
    )
    start = body.find(TASK_START)
    end = body.find(TASK_END)
    if start >= 0 and end > start:
        end += len(TASK_END)
        return body[:start].rstrip() + "\n\n" + block + body[end:]
    prefix = body.rstrip()
    return (prefix + "\n\n" if prefix else "") + block + "\n"


def context_decision(
    manifest: Mapping[str, Any],
    current_shas: Mapping[str, str],
    *,
    scope_changed: bool = False,
    base_changed_materially: bool = False,
    rebuild_ratio: float = 0.5,
) -> dict[str, Any]:
    validate_task_manifest(manifest)
    if scope_changed:
        return {"state": "CONTEXT_REBUILD", "changed_files": [], "reason": "task-scope-changed"}
    if base_changed_materially:
        return {"state": "CONTEXT_REBUILD", "changed_files": [], "reason": "base-changed-materially"}
    observed = manifest["context"].get("observed_files", [])
    if not observed:
        return {"state": "CONTEXT_REBUILD", "changed_files": [], "reason": "no-observed-files"}
    changed = [item["path"] for item in observed if current_shas.get(item["path"]) != item["sha"]]
    if not changed:
        return {"state": "CONTEXT_HIT", "changed_files": [], "reason": "observed-files-unchanged"}
    ratio = len(changed) / len(observed)
    if ratio > rebuild_ratio:
        return {"state": "CONTEXT_REBUILD", "changed_files": sorted(changed), "reason": "too-many-observed-files-changed"}
    return {"state": "CONTEXT_REFRESH", "changed_files": sorted(changed), "reason": "bounded-file-delta"}


def update_observed_shas(manifest: Mapping[str, Any], current_shas: Mapping[str, str]) -> dict[str, Any]:
    result = deepcopy(dict(manifest))
    for item in result["context"].get("observed_files", []):
        if item["path"] in current_shas:
            item["sha"] = current_shas[item["path"]]
    validate_task_manifest(result)
    return result
