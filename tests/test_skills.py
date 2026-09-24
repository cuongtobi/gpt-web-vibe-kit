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

    def test_session_skill_documents_context_states_and_hard_budget(self):
        root = Path(__file__).resolve().parents[1]
        text = (root / "skills/session/SKILL.md").read_text(encoding="utf-8")
        for state in ("CONTEXT_HIT", "CONTEXT_REFRESH", "CONTEXT_REBUILD"):
            self.assertIn(state, text)
        self.assertIn("hard budget", text.lower())
        self.assertIn("schema_version: 2", text)

    def test_plan_skill_documents_iterative_symbol_search(self):
        root = Path(__file__).resolve().parents[1]
        text = (root / "skills/plan/SKILL.md").read_text(encoding="utf-8")
        self.assertIn("iterative", text.lower())
        self.assertIn("context.symbols", text)

    def test_verify_skill_requires_current_head(self):
        root = Path(__file__).resolve().parents[1]
        text = (root / "skills/verify/SKILL.md").read_text(encoding="utf-8")
        self.assertIn("current PR head", text)
        self.assertIn("verification.head_sha", text)
        self.assertIn("PASS_VERIFIED", text)

    def test_comment_and_security_policies_are_wired_into_workflow(self):
        root = Path(__file__).resolve().parents[1]
        build = (root / "skills/build/SKILL.md").read_text(encoding="utf-8")
        plan = (root / "skills/plan/SKILL.md").read_text(encoding="utf-8")
        verify = (root / "skills/verify/SKILL.md").read_text(encoding="utf-8")
        review = (root / "skills/github-review/SKILL.md").read_text(encoding="utf-8")
        self.assertIn("Comment and documentation policy", build)
        self.assertIn("security-sensitive", plan)
        self.assertIn("security evidence", verify.lower())
        self.assertIn("security.evidence", review)

    def test_vibe_skill_lists_test_and_docs_modes(self):
        root = Path(__file__).resolve().parents[1]
        text = (root / "skills/vibe/SKILL.md").read_text(encoding="utf-8")
        self.assertIn("`test`", text)
        self.assertIn("`docs`", text)


if __name__ == "__main__":
    unittest.main()
