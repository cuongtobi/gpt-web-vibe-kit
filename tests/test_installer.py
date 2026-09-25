import json
import tempfile
import unittest
from pathlib import Path

import install


class InstallerTests(unittest.TestCase):
    def test_install_creates_contract_detects_context_and_preserves_agents(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            (target / "AGENTS.md").write_text("user instructions\n", encoding="utf-8")
            (target / "requirements.txt").write_text("fastapi\npytest\n", encoding="utf-8")
            (target / "app.py").write_text("from fastapi import FastAPI\n", encoding="utf-8")
            actions = install.install(target)
            self.assertTrue((target / ".vibe/config.json").exists())
            self.assertTrue((target / ".vibe/project-context.json").exists())
            self.assertTrue((target / ".vibe/README.md").exists())
            self.assertEqual((target / "AGENTS.md").read_text(encoding="utf-8"), "user instructions\n")
            self.assertIn("preserve AGENTS.md", actions)
            self.assertIn("detect project context", actions)
            config = json.loads((target / ".vibe/config.json").read_text(encoding="utf-8"))
            self.assertEqual(config["workflow"], "github-native")
            self.assertEqual(config["manifest_schema_version"], 2)
            context = json.loads((target / ".vibe/project-context.json").read_text(encoding="utf-8"))
            self.assertIn("python", context["languages"])
            self.assertIn("fastapi", context["frameworks"])
            self.assertIn("pytest", context["verification"]["commands"])

    def test_new_project_agents_include_behavioral_policy(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            install.install(target)
            agents = (target / "AGENTS.md").read_text(encoding="utf-8")
            self.assertIn("## Behavioral coding policy", agents)
            self.assertIn("Think before coding", agents)
            self.assertIn("Changed-line traceability", agents)

    def test_dry_run_writes_nothing(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            actions = install.install(target, dry_run=True)
            self.assertIn("write .vibe/config.json", actions)
            self.assertIn("detect project context", actions)
            self.assertFalse((target / ".vibe").exists())
            self.assertFalse((target / "AGENTS.md").exists())

    def test_force_updates_vibe_files_but_never_agents(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            (target / ".vibe").mkdir()
            (target / ".vibe/config.json").write_text('{"custom": true}', encoding="utf-8")
            (target / ".vibe/project-context.json").write_text('{"custom": true}', encoding="utf-8")
            (target / ".vibe/README.md").write_text("old", encoding="utf-8")
            (target / "AGENTS.md").write_text("keep me", encoding="utf-8")
            install.install(target, force=True)
            config = json.loads((target / ".vibe/config.json").read_text(encoding="utf-8"))
            self.assertEqual(config["workflow"], "github-native")
            self.assertEqual((target / "AGENTS.md").read_text(encoding="utf-8"), "keep me")


if __name__ == "__main__":
    unittest.main()
