import json
import unittest
from pathlib import Path

from runtime.state import (
    ManifestError,
    TASK_END,
    TASK_START,
    context_decision,
    extract_task_manifest,
    render_task_manifest,
    validate_project_context,
    validate_task_manifest,
)


def task_manifest():
    return {
        "schema_version": 1,
        "task_id": "jwt-refresh",
        "mode": "bug_fix",
        "status": "building",
        "request": "Fix refresh token after session expiry",
        "targets": ["app/auth.py"],
        "context": {
            "dependencies": ["app/token.py"],
            "consumers": ["app/api.py"],
            "tests": ["tests/test_auth.py"],
            "config_files": [],
            "observed_files": [
                {"path": "app/auth.py", "sha": "aaa"},
                {"path": "app/token.py", "sha": "bbb"},
                {"path": "app/api.py", "sha": "ccc"},
                {"path": "tests/test_auth.py", "sha": "ddd"},
            ],
        },
        "acceptance": [
            {"id": "AC1", "expected": "Refresh succeeds", "evidence": "", "status": "pending"}
        ],
    }


class StateTests(unittest.TestCase):
    def test_task_manifest_round_trip_in_pr_body(self):
        manifest = task_manifest()
        rendered = render_task_manifest("# Fix token\n\nHuman summary.", manifest)
        self.assertIn(TASK_START, rendered)
        self.assertIn(TASK_END, rendered)
        self.assertEqual(extract_task_manifest(rendered), manifest)

    def test_render_replaces_manifest_without_duplicate(self):
        first = render_task_manifest("summary", task_manifest())
        updated = task_manifest()
        updated["status"] = "verifying"
        second = render_task_manifest(first, updated)
        self.assertEqual(second.count(TASK_START), 1)
        self.assertEqual(extract_task_manifest(second)["status"], "verifying")

    def test_context_hit_when_observed_files_unchanged(self):
        result = context_decision(task_manifest(), {
            "app/auth.py": "aaa", "app/token.py": "bbb",
            "app/api.py": "ccc", "tests/test_auth.py": "ddd",
        })
        self.assertEqual(result["state"], "CONTEXT_HIT")

    def test_context_refresh_for_bounded_delta(self):
        result = context_decision(task_manifest(), {
            "app/auth.py": "changed", "app/token.py": "bbb",
            "app/api.py": "ccc", "tests/test_auth.py": "ddd",
        })
        self.assertEqual(result["state"], "CONTEXT_REFRESH")
        self.assertEqual(result["changed_files"], ["app/auth.py"])

    def test_context_rebuild_when_majority_changed(self):
        result = context_decision(task_manifest(), {
            "app/auth.py": "x", "app/token.py": "y",
            "app/api.py": "z", "tests/test_auth.py": "ddd",
        })
        self.assertEqual(result["state"], "CONTEXT_REBUILD")

    def test_scope_change_forces_rebuild(self):
        result = context_decision(task_manifest(), {}, scope_changed=True)
        self.assertEqual(result["state"], "CONTEXT_REBUILD")

    def test_duplicate_acceptance_ids_rejected(self):
        manifest = task_manifest()
        manifest["acceptance"].append(dict(manifest["acceptance"][0]))
        with self.assertRaises(ManifestError):
            validate_task_manifest(manifest)

    def test_project_context_template_valid(self):
        root = Path(__file__).resolve().parents[1]
        data = json.loads((root / "templates/project/.vibe/project-context.json").read_text(encoding="utf-8"))
        validate_project_context(data)
