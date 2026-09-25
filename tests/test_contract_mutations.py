import json
import unittest
from pathlib import Path

from runtime.state import ManifestError, validate_task_manifest, validate_vibe_config

ROOT = Path(__file__).resolve().parents[1]


def task_template():
    return json.loads((ROOT / "templates/task.json").read_text(encoding="utf-8"))


def config_template():
    return json.loads((ROOT / "templates/project/.vibe/config.json").read_text(encoding="utf-8"))


class ContractMutationTests(unittest.TestCase):
    def test_manifest_mutations_cannot_create_false_pass(self):
        base = task_template()
        base["request"] = "Update author profile copy"
        base["acceptance"][0]["status"] = "met"
        base["acceptance"][0]["evidence"] = [{"type": "test", "ref": "tests:test"}]
        base["verification"] = {
            "commands": ["python -m unittest"],
            "head_sha": base["head_sha"],
            "ci_run_id": 1,
            "status": "PASS_VERIFIED",
        }
        validate_task_manifest(base)

        mutations = []

        pending = json.loads(json.dumps(base))
        pending["acceptance"][0]["status"] = "pending"
        mutations.append(("pending acceptance", pending))

        no_evidence = json.loads(json.dumps(base))
        no_evidence["acceptance"][0]["evidence"] = []
        mutations.append(("missing acceptance evidence", no_evidence))

        security_bypass = json.loads(json.dumps(base))
        security_bypass["request"] = "Fix refresh token after session expiry"
        security_bypass["security"]["classification"] = "standard"
        security_bypass["security"]["candidate_disposition"] = None
        mutations.append(("security candidate bypass", security_bypass))

        frontend_gap = json.loads(json.dumps(base))
        frontend_gap["frontend"] = {
            "surface": "application",
            "intent": "refine",
            "design_context": {"path": None, "mode": "infer-existing-ui"},
            "acceptance_dimensions": ["responsive-behavior"],
            "visual_qa": {
                "max_rounds": 2,
                "browser_tooling": [],
                "evidence": [],
                "head_sha": None,
                "limitations": [],
            },
        }
        mutations.append(("unbound frontend acceptance", frontend_gap))

        for label, mutated in mutations:
            with self.subTest(label=label):
                with self.assertRaises(ManifestError):
                    validate_task_manifest(mutated)

    def test_config_mutations_are_rejected(self):
        base = config_template()
        mutations = []

        unknown = json.loads(json.dumps(base))
        unknown["context"]["infinite_context"] = True
        mutations.append(("unknown context field", unknown))

        rounds = json.loads(json.dumps(base))
        rounds["context"]["max_search_rounds"] = 0
        mutations.append(("zero search rounds", rounds))

        commands = json.loads(json.dumps(base))
        commands["verification"]["require_commands"] = "true"
        mutations.append(("non-boolean require_commands", commands))

        schema_version = json.loads(json.dumps(base))
        schema_version["manifest_schema_version"] = 1
        mutations.append(("wrong manifest schema version", schema_version))

        for label, mutated in mutations:
            with self.subTest(label=label):
                with self.assertRaises(ManifestError):
                    validate_vibe_config(mutated)


if __name__ == "__main__":
    unittest.main()
