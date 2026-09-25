import json
import subprocess
import tempfile
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class CliTests(unittest.TestCase):
    def run_cli(self, *args):
        return subprocess.run(
            [sys.executable, str(ROOT / "runtime" / "vibe_web.py"), *args],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            check=False,
        )

    def test_direct_cli_validates_project_context(self):
        result = self.run_cli(
            "validate-project",
            str(ROOT / "templates" / "project" / ".vibe" / "project-context.json"),
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(result.stdout.strip(), "OK")

    def test_direct_cli_validates_config(self):
        result = self.run_cli(
            "validate-config",
            str(ROOT / "templates" / "project" / ".vibe" / "config.json"),
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(result.stdout.strip(), "OK")

    def test_completion_status_reports_incomplete_task(self):
        result = self.run_cli(
            "completion-status",
            str(ROOT / "templates" / "task.json"),
            "--config",
            str(ROOT / "templates" / "project" / ".vibe" / "config.json"),
        )
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        data = json.loads(result.stdout)
        self.assertFalse(data["ok"])
        self.assertTrue(data["violations"])

    def test_detect_project_cli(self):
        result = self.run_cli("detect-project", str(ROOT / "tests" / "fixtures" / "fastapi-small"))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        data = json.loads(result.stdout)
        self.assertIn("fastapi", data["frameworks"])


if __name__ == "__main__":
    unittest.main()
