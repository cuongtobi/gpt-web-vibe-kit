import json
import unittest
from copy import deepcopy
from pathlib import Path

from jsonschema import Draft202012Validator

from runtime.state import (
    ManifestError,
    validate_project_context,
    validate_task_manifest,
    validate_vibe_config,
)

ROOT = Path(__file__).resolve().parents[1]


def load_json(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


class SchemaContractTests(unittest.TestCase):
    def setUp(self):
        self.task_schema = load_json("schemas/task.schema.json")
        self.project_schema = load_json("schemas/project-context.schema.json")
        self.config_schema = load_json("schemas/config.schema.json")

    def test_templates_validate_against_json_schemas(self):
        pairs = (
            ("templates/task.json", self.task_schema),
            ("templates/project/.vibe/project-context.json", self.project_schema),
            ("templates/project/.vibe/config.json", self.config_schema),
        )
        for path, schema in pairs:
            with self.subTest(path=path):
                Draft202012Validator(schema).validate(load_json(path))

    def test_task_schema_and_runtime_reject_duplicate_targets(self):
        task = load_json("templates/task.json")
        task["targets"] = ["app.py", "app.py"]
        with self.assertRaises(Exception):
            Draft202012Validator(self.task_schema).validate(task)
        with self.assertRaises(ManifestError):
            validate_task_manifest(task)

    def test_project_schema_and_runtime_reject_unknown_nested_field(self):
        project = load_json("templates/project/.vibe/project-context.json")
        project["project"]["unexpected"] = True
        with self.assertRaises(Exception):
            Draft202012Validator(self.project_schema).validate(project)
        with self.assertRaises(ManifestError):
            validate_project_context(project)

    def test_config_schema_and_runtime_reject_unknown_policy_field(self):
        config = load_json("templates/project/.vibe/config.json")
        config["context"]["unbounded_search"] = True
        with self.assertRaises(Exception):
            Draft202012Validator(self.config_schema).validate(config)
        with self.assertRaises(ManifestError):
            validate_vibe_config(config)

    def test_frontend_acceptance_map_is_schema_valid(self):
        task = load_json("templates/task.json")
        task["acceptance"][0]["status"] = "met"
        task["acceptance"][0]["evidence"] = [{"type": "test", "ref": "ui:test"}]
        task["security"]["candidate_disposition"] = "no security candidate in this synthetic UI request"
        task["request"] = "Refine responsive navigation layout"
        task["frontend"] = {
            "surface": "application",
            "intent": "refine",
            "design_context": {"path": None, "mode": "infer-existing-ui"},
            "acceptance_dimensions": ["responsive-behavior"],
            "acceptance_map": {"responsive-behavior": ["AC1"]},
            "visual_qa": {
                "max_rounds": 2,
                "browser_tooling": [],
                "evidence": [],
                "head_sha": None,
                "limitations": ["browser tooling unavailable"],
            },
        }
        Draft202012Validator(self.task_schema).validate(task)
        validate_task_manifest(task)


if __name__ == "__main__":
    unittest.main()
