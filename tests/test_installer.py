import json
import tempfile
import unittest
from pathlib import Path

import install


class InstallerTests(unittest.TestCase):
    def test_install_creates_contract_and_preserves_agents(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            (target / "AGENTS.md").write_text("user instructions\n", encoding="utf-8")
            actions = install.install(target)
            self.assertTrue((target / ".vibe/config.json").exists())
            self.assertTrue((target / ".vibe/project-context.json").exists())
            self.assertTrue((target / ".vibe/README.md").exists())
            self.assertEqual((target / "AGENTS.md").read_text(encoding="utf-8"), "user instructions\n")
            self.assertIn("preserve AGENTS.md", actions)
            config = json.loads((target / ".vibe/config.json").read_text(encoding="utf-8"))
            self.assertEqual(config["workflow"], "github-native")
            self.assertEqual(config["github"]["task_state"], "pull_request_body")

    def test_dry_run_writes_nothing(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            actions = install.install(target, dry_run=True)
            self.assertIn("write .vibe/config.json", actions)
            self.assertFalse((target / ".vibe").exists())
            self.assertFalse((target / "AGENTS.md").exists())

    def test_force_updates_vibe_files_but_never_agents(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            (target / ".vibe").mkdir()
            (target / ".vibe/config.json").write_text('{"custom": true}', encoding="utf-8")
            (target / "AGENTS.md").write_text("keep me", encoding="utf-8")
            install.install(target, force=True)
            config = json.loads((target / ".vibe/config.json").read_text(encoding="utf-8"))
            self.assertEqual(config["workflow"], "github-native")
            self.assertEqual((target / "AGENTS.md").read_text(encoding="utf-8"), "keep me")
