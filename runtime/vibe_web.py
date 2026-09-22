from __future__ import annotations

import argparse
import json
from pathlib import Path

try:
    from runtime.state import context_decision, extract_task_manifest, validate_project_context, validate_task_manifest
except ModuleNotFoundError:  # direct execution: python runtime/vibe_web.py
    from state import context_decision, extract_task_manifest, validate_project_context, validate_task_manifest


def _load_json(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return data


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate gpt-web-vibe-kit state artifacts.")
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("validate-project"); p.add_argument("path", type=Path)
    p = sub.add_parser("validate-task"); p.add_argument("path", type=Path)
    p = sub.add_parser("validate-pr-body"); p.add_argument("path", type=Path)
    p = sub.add_parser("context-status")
    p.add_argument("task", type=Path); p.add_argument("current_shas", type=Path)
    p.add_argument("--scope-changed", action="store_true")
    p.add_argument("--base-changed-materially", action="store_true")
    args = parser.parse_args()
    if args.command == "validate-project":
        validate_project_context(_load_json(args.path)); print("OK"); return 0
    if args.command == "validate-task":
        validate_task_manifest(_load_json(args.path)); print("OK"); return 0
    if args.command == "validate-pr-body":
        extract_task_manifest(args.path.read_text(encoding="utf-8")); print("OK"); return 0
    if args.command == "context-status":
        print(json.dumps(context_decision(
            _load_json(args.task), _load_json(args.current_shas),
            scope_changed=args.scope_changed,
            base_changed_materially=args.base_changed_materially,
        ), indent=2, sort_keys=True))
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
