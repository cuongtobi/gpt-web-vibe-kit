from __future__ import annotations

import argparse
import json
from pathlib import Path

try:
    from runtime.state import (
        completion_violations,
        completion_violations,
        context_budget_violations,
        context_decision,
        extract_task_manifest,
        validate_project_context,
        validate_task_manifest,
        validate_vibe_config,
    )
    from install import detect_project_context
except ModuleNotFoundError:  # direct execution: python runtime/vibe_web.py
    from state import (
        context_budget_violations,
        context_decision,
        extract_task_manifest,
        validate_project_context,
        validate_task_manifest,
        validate_vibe_config,
    )
    from pathlib import Path as _Path
    import sys as _sys
    _sys.path.insert(0, str(_Path(__file__).resolve().parents[1]))
    from install import detect_project_context


def _load_json(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return data


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate gpt-web-vibe-kit state artifacts.")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("validate-project")
    p.add_argument("path", type=Path)

    p = sub.add_parser("validate-config")
    p.add_argument("path", type=Path)

    p = sub.add_parser("validate-task")
    p.add_argument("path", type=Path)
    p.add_argument("--config", type=Path)

    p = sub.add_parser("validate-pr-body")
    p.add_argument("path", type=Path)
    p.add_argument("--config", type=Path)

    p = sub.add_parser("context-status")
    p.add_argument("task", type=Path)
    p.add_argument("current_shas", type=Path)
    p.add_argument("--config", type=Path)
    p.add_argument("--scope-changed", action="store_true")
    p.add_argument("--base-changed-materially", action="store_true")

    p = sub.add_parser("budget-status")
    p.add_argument("task", type=Path)
    p.add_argument("--config", type=Path)

    p = sub.add_parser("completion-status")
    p.add_argument("task", type=Path)
    p.add_argument("--config", type=Path)

    p = sub.add_parser("detect-project")
    p.add_argument("path", type=Path)

    args = parser.parse_args()

    if args.command == "validate-project":
        validate_project_context(_load_json(args.path))
        print("OK")
        return 0

    if args.command == "validate-config":
        validate_vibe_config(_load_json(args.path))
        print("OK")
        return 0

    if args.command == "validate-task":
        task = _load_json(args.path)
        validate_task_manifest(task)
        config = _load_json(args.config) if args.config else None
        violations = context_budget_violations(task, config)
        if task.get("verification", {}).get("status") == "PASS_VERIFIED" or task.get("status") in {"ready", "complete"}:
            violations.extend(completion_violations(task, config))
        if violations:
            raise ValueError("; ".join(violations))
        print("OK")
        return 0

    if args.command == "validate-pr-body":
        task = extract_task_manifest(args.path.read_text(encoding="utf-8"))
        config = _load_json(args.config) if args.config else None
        violations = context_budget_violations(task, config)
        if task.get("verification", {}).get("status") == "PASS_VERIFIED" or task.get("status") in {"ready", "complete"}:
            violations.extend(completion_violations(task, config))
        if violations:
            raise ValueError("; ".join(violations))
        print("OK")
        return 0

    if args.command == "context-status":
        config = _load_json(args.config) if args.config else None
        print(json.dumps(context_decision(
            _load_json(args.task),
            _load_json(args.current_shas),
            config=config,
            scope_changed=args.scope_changed,
            base_changed_materially=args.base_changed_materially,
        ), indent=2, sort_keys=True))
        return 0

    if args.command == "budget-status":
        config = _load_json(args.config) if args.config else None
        violations = context_budget_violations(_load_json(args.task), config)
        print(json.dumps({"ok": not violations, "violations": violations}, indent=2, sort_keys=True))
        return 0 if not violations else 1

    if args.command == "completion-status":
        config = _load_json(args.config) if args.config else None
        violations = completion_violations(_load_json(args.task), config)
        print(json.dumps({"ok": not violations, "violations": violations}, indent=2, sort_keys=True))
        return 0 if not violations else 1

    if args.command == "detect-project":
        print(json.dumps(detect_project_context(args.path), indent=2, sort_keys=True))
        return 0

    return 2


if __name__ == "__main__":
    raise SystemExit(main())
