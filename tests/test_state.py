import json
import unittest
from pathlib import Path

from runtime.state import (
    ManifestError,
    TASK_END,
    TASK_START,
    context_budget_violations,
    context_decision,
    extract_task_manifest,
    render_task_manifest,
    update_manifest_head,
    validate_project_context,
    validate_task_manifest,
    validate_vibe_config,
    verification_is_current,
)


def task_manifest():
    return {
        "schema_version": 2,
        "task_id": "jwt-refresh",
        "mode": "bug_fix",
        "status": "building",
        "request": "Fix refresh token after session expiry",
        "base_branch": "main",
        "base_sha": "base123",
        "head_branch": "vibe/bug_fix/jwt-refresh",
        "head_sha": "head123",
        "targets": ["app/auth.py"],
        "context": {
            "symbols": ["refresh_access_token"],
            "dependencies": ["app/token.py"],
            "consumers": ["app/api.py"],
            "tests": ["tests/test_auth.py"],
            "config_files": [],
            "observed_files": [
                {"path": "app/auth.py", "sha": "aaa", "role": "target", "depth": 0, "symbols": ["refresh_access_token"]},
                {"path": "app/token.py", "sha": "bbb", "role": "dependency", "depth": 1, "symbols": ["decode_refresh_token"]},
                {"path": "app/api.py", "sha": "ccc", "role": "consumer", "depth": 1, "symbols": []},
                {"path": "tests/test_auth.py", "sha": "ddd", "role": "test", "depth": 1, "symbols": ["test_refresh_after_session_expiry"]},
            ],
        },
        "acceptance": [{"id": "AC1", "expected": "Refresh succeeds", "status": "pending", "evidence": []}],
        "verification": {"commands": ["pytest tests/test_auth.py"], "head_sha": None, "ci_run_id": None, "status": None},
        "security": {
            "classification": "standard",
            "surfaces": [],
            "trust_boundaries": [],
            "abuse_cases": [],
            "controls": [],
            "evidence": [],
            "head_sha": None,
            "limitations": [],
        },
        "uncertainties": [],
    }


def config(**overrides):
    context = {"max_dependency_depth": 2,"max_source_files": 15,"max_test_files": 6,"max_related_modules": 6,"rebuild_changed_ratio": 0.5}
    context.update(overrides)
    return {"version": 2,"context": context,"verification": {"commands": []}}


class StateTests(unittest.TestCase):
    def test_task_manifest_round_trip_in_pr_body(self):
        manifest = task_manifest(); rendered = render_task_manifest("# Fix token\n\nHuman summary.", manifest)
        self.assertIn(TASK_START, rendered); self.assertIn(TASK_END, rendered); self.assertEqual(extract_task_manifest(rendered), manifest)

    def test_render_replaces_manifest_without_duplicate(self):
        first = render_task_manifest("summary", task_manifest()); updated = task_manifest(); updated["status"] = "verifying"
        second = render_task_manifest(first, updated); self.assertEqual(second.count(TASK_START), 1); self.assertEqual(extract_task_manifest(second)["status"], "verifying")

    def test_duplicate_manifest_is_rejected(self):
        rendered = render_task_manifest("summary", task_manifest())
        with self.assertRaises(ManifestError): extract_task_manifest(rendered + "\n" + rendered)

    def test_duplicate_marker_is_rejected_on_render(self):
        rendered = render_task_manifest("summary", task_manifest())
        with self.assertRaises(ManifestError): render_task_manifest(rendered + "\n" + TASK_START, task_manifest())

    def test_v1_manifest_is_rejected(self):
        manifest = task_manifest(); manifest["schema_version"] = 1
        with self.assertRaises(ManifestError): validate_task_manifest(manifest)

    def test_test_and_docs_modes_are_valid(self):
        for mode in ("test", "docs"):
            manifest = task_manifest(); manifest["mode"] = mode; validate_task_manifest(manifest)

    def test_referenced_files_must_be_observed(self):
        manifest = task_manifest(); manifest["context"]["dependencies"].append("app/missing.py")
        with self.assertRaises(ManifestError): validate_task_manifest(manifest)

    def test_context_hit_when_observed_files_unchanged(self):
        result = context_decision(task_manifest(), {"app/auth.py":"aaa","app/token.py":"bbb","app/api.py":"ccc","tests/test_auth.py":"ddd"}, config=config())
        self.assertEqual(result["state"], "CONTEXT_HIT")

    def test_context_refresh_for_bounded_delta(self):
        result = context_decision(task_manifest(), {"app/auth.py":"changed","app/token.py":"bbb","app/api.py":"ccc","tests/test_auth.py":"ddd"}, config=config())
        self.assertEqual(result["state"], "CONTEXT_REFRESH"); self.assertEqual(result["changed_files"], ["app/auth.py"])

    def test_context_rebuild_when_majority_changed(self):
        result = context_decision(task_manifest(), {"app/auth.py":"x","app/token.py":"y","app/api.py":"z","tests/test_auth.py":"ddd"}, config=config())
        self.assertEqual(result["state"], "CONTEXT_REBUILD")

    def test_configured_rebuild_ratio_is_used(self):
        result = context_decision(task_manifest(), {"app/auth.py":"changed","app/token.py":"bbb","app/api.py":"ccc","tests/test_auth.py":"ddd"}, config=config(rebuild_changed_ratio=0.1))
        self.assertEqual(result["state"], "CONTEXT_REBUILD")

    def test_budget_violation_for_dependency_depth(self):
        manifest = task_manifest(); manifest["context"]["observed_files"][1]["depth"] = 3
        violations = context_budget_violations(manifest, config(max_dependency_depth=2)); self.assertTrue(any("dependency depth" in item for item in violations))
        result = context_decision(manifest, {}, config=config(max_dependency_depth=2)); self.assertEqual(result["reason"], "context-budget-exceeded")

    def test_budget_violation_for_source_files(self):
        self.assertTrue(any("source files" in item for item in context_budget_violations(task_manifest(), config(max_source_files=2))))

    def test_scope_change_forces_rebuild(self):
        self.assertEqual(context_decision(task_manifest(), {}, config=config(), scope_changed=True)["state"], "CONTEXT_REBUILD")

    def test_duplicate_acceptance_ids_rejected(self):
        manifest = task_manifest(); manifest["acceptance"].append(dict(manifest["acceptance"][0]))
        with self.assertRaises(ManifestError): validate_task_manifest(manifest)

    def test_pass_verified_requires_current_head(self):
        manifest = task_manifest(); manifest["verification"] = {"commands":["pytest"],"head_sha":"old","ci_run_id":123,"status":"PASS_VERIFIED"}
        with self.assertRaises(ManifestError): validate_task_manifest(manifest)

    def test_verification_current_helper(self):
        manifest = task_manifest(); manifest["verification"] = {"commands":["pytest"],"head_sha":"head123","ci_run_id":123,"status":"PASS_VERIFIED"}
        self.assertTrue(verification_is_current(manifest))

    def test_new_head_invalidates_pass(self):
        manifest = task_manifest(); manifest["verification"] = {"commands":["pytest"],"head_sha":"head123","ci_run_id":123,"status":"PASS_VERIFIED"}
        updated = update_manifest_head(manifest, "head456"); self.assertEqual(updated["head_sha"], "head456"); self.assertIsNone(updated["verification"]["status"]); self.assertIsNone(updated["verification"]["ci_run_id"])

    def test_legacy_v2_manifest_without_security_remains_valid(self):
        manifest = task_manifest(); manifest.pop("security")
        validate_task_manifest(manifest)

    def test_security_sensitive_pass_requires_current_security_evidence(self):
        manifest = task_manifest()
        manifest["security"].update({
            "classification": "security-sensitive",
            "surfaces": ["authentication/session/token"],
            "trust_boundaries": ["refresh token -> session renewal"],
            "abuse_cases": ["replay revoked refresh token"],
            "controls": ["rotation and revocation"],
        })
        manifest["verification"] = {"commands":["pytest"],"head_sha":"head123","ci_run_id":123,"status":"PASS_VERIFIED"}
        with self.assertRaises(ManifestError):
            validate_task_manifest(manifest)
        manifest["security"]["evidence"] = [{"type":"test","ref":"tests/test_auth.py::test_replay_rejected"}]
        manifest["security"]["head_sha"] = "head123"
        validate_task_manifest(manifest)
        self.assertTrue(verification_is_current(manifest))

    def test_security_sensitive_manifest_requires_surface(self):
        manifest = task_manifest()
        manifest["security"]["classification"] = "security-sensitive"
        with self.assertRaises(ManifestError):
            validate_task_manifest(manifest)

    def test_new_head_invalidates_security_evidence(self):
        manifest = task_manifest()
        manifest["security"].update({
            "classification": "security-sensitive",
            "surfaces": ["file upload/filesystem"],
            "trust_boundaries": ["HTTP upload -> storage"],
            "abuse_cases": ["path traversal"],
            "controls": ["normalized server-side storage path"],
            "evidence": [{"type":"test","ref":"tests/test_upload.py::test_rejects_traversal"}],
            "head_sha": "head123",
        })
        manifest["verification"] = {"commands":["pytest"],"head_sha":"head123","ci_run_id":123,"status":"PASS_VERIFIED"}
        updated = update_manifest_head(manifest, "head456")
        self.assertIsNone(updated["security"]["head_sha"])
        self.assertEqual(updated["security"]["evidence"], [])
        self.assertIsNone(updated["verification"]["status"])

    def test_frontend_manifest_is_optional_and_valid(self):
        manifest = task_manifest()
        validate_task_manifest(manifest)
        manifest["frontend"] = {
            "surface": "component",
            "intent": "redesign",
            "design_context": {"path": "DESIGN.md", "mode": "declared"},
            "acceptance_dimensions": [
                "visual-consistency",
                "responsive-behavior",
                "accessibility",
            ],
            "visual_qa": {
                "max_rounds": 2,
                "browser_tooling": ["playwright"],
                "evidence": [],
                "head_sha": None,
                "limitations": [],
            },
        }
        validate_task_manifest(manifest)

    def test_frontend_acceptance_dimensions_reject_non_strings(self):
        manifest = task_manifest()
        manifest["frontend"] = {
            "surface": "application",
            "intent": "refine",
            "design_context": {"path": None, "mode": "infer-existing-ui"},
            "acceptance_dimensions": [{"unexpected": "object"}],
            "visual_qa": {
                "max_rounds": 2,
                "browser_tooling": [],
                "evidence": [],
                "head_sha": None,
                "limitations": [],
            },
        }
        with self.assertRaises(ManifestError):
            validate_task_manifest(manifest)

    def test_frontend_visual_qa_is_bounded(self):
        manifest = task_manifest()
        manifest["frontend"] = {
            "surface": "application",
            "intent": "refine",
            "design_context": {"path": None, "mode": "infer-existing-ui"},
            "acceptance_dimensions": ["visual-consistency"],
            "visual_qa": {
                "max_rounds": 3,
                "browser_tooling": [],
                "evidence": [],
                "head_sha": None,
                "limitations": [],
            },
        }
        with self.assertRaises(ManifestError):
            validate_task_manifest(manifest)

    def test_frontend_visual_evidence_requires_current_head(self):
        manifest = task_manifest()
        manifest["frontend"] = {
            "surface": "marketing",
            "intent": "redesign",
            "design_context": {"path": None, "mode": "infer-existing-ui"},
            "acceptance_dimensions": ["visual-consistency", "responsive-behavior"],
            "visual_qa": {
                "max_rounds": 2,
                "browser_tooling": ["playwright"],
                "evidence": [{"type": "screenshot", "ref": "artifact://desktop-home"}],
                "head_sha": "old-head",
                "limitations": [],
            },
        }
        with self.assertRaises(ManifestError):
            validate_task_manifest(manifest)
        manifest["frontend"]["visual_qa"]["head_sha"] = "head123"
        validate_task_manifest(manifest)

    def test_new_head_invalidates_frontend_visual_evidence(self):
        manifest = task_manifest()
        manifest["frontend"] = {
            "surface": "component",
            "intent": "refine",
            "design_context": {"path": None, "mode": "infer-existing-ui"},
            "acceptance_dimensions": ["interaction-states", "accessibility"],
            "visual_qa": {
                "max_rounds": 2,
                "browser_tooling": ["cypress"],
                "evidence": [{"type": "browser-check", "ref": "cypress:navbar"}],
                "head_sha": "head123",
                "limitations": [],
            },
        }
        updated = update_manifest_head(manifest, "head456")
        self.assertIsNone(updated["frontend"]["visual_qa"]["head_sha"])
        self.assertEqual(updated["frontend"]["visual_qa"]["evidence"], [])

    def test_project_context_template_valid(self):
        root = Path(__file__).resolve().parents[1]; data = json.loads((root / "templates/project/.vibe/project-context.json").read_text(encoding="utf-8")); validate_project_context(data)

    def test_config_template_valid(self):
        root = Path(__file__).resolve().parents[1]; data = json.loads((root / "templates/project/.vibe/config.json").read_text(encoding="utf-8")); validate_vibe_config(data)

    def test_task_template_valid(self):
        root = Path(__file__).resolve().parents[1]; data = json.loads((root / "templates/task.json").read_text(encoding="utf-8")); validate_task_manifest(data)


if __name__ == "__main__": unittest.main()
