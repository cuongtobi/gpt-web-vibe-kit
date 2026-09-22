import unittest
from pathlib import Path


class SkillTests(unittest.TestCase):
    def test_core_skills_have_frontmatter_and_required_contracts(self):
        root = Path(__file__).resolve().parents[1]
        names = ["bootstrap", "session", "vibe", "plan", "build", "verify", "github-review"]
        for name in names:
            with self.subTest(name=name):
                text = (root / "skills" / name / "SKILL.md").read_text(encoding="utf-8")
                self.assertTrue(text.startswith("---\n"))
                self.assertIn(f"name: {name}\n", text)
                self.assertIn("description:", text)

    def test_session_skill_documents_context_states(self):
        root = Path(__file__).resolve().parents[1]
        text = (root / "skills/session/SKILL.md").read_text(encoding="utf-8")
        for state in ("CONTEXT_HIT", "CONTEXT_REFRESH", "CONTEXT_REBUILD"):
            self.assertIn(state, text)

    def test_verify_skill_requires_current_head(self):
        root = Path(__file__).resolve().parents[1]
        text = (root / "skills/verify/SKILL.md").read_text(encoding="utf-8")
        self.assertIn("current PR head", text)
        self.assertIn("PASS_VERIFIED", text)
