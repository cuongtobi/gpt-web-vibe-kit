import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class CliTests(unittest.TestCase):
    def test_direct_cli_validates_project_context(self):
        result = subprocess.run(
            [
                sys.executable,
                str(ROOT / "runtime" / "vibe_web.py"),
                "validate-project",
                str(ROOT / "templates" / "project" / ".vibe" / "project-context.json"),
            ],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(result.stdout.strip(), "OK")


if __name__ == "__main__":
    unittest.main()
