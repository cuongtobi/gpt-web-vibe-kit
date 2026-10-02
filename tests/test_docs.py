import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

EXPECTED_DOCS = [
    "docs/workflows/new-task.md",
    "docs/workflows/continue-task.md",
    "docs/workflows/bug-fix.md",
    "docs/workflows/feature-change.md",
    "docs/workflows/refactor.md",
    "docs/workflows/test-only.md",
    "docs/workflows/docs-only.md",
    "docs/workflows/frontend.md",
    "docs/operations/ci-failure.md",
    "docs/operations/review.md",
    "docs/operations/rebase.md",
    "docs/operations/merge.md",
    "docs/operations/concurrent-tasks.md",
    "docs/reference/task-manifest.md",
    "docs/reference/context.md",
    "docs/reference/verification.md",
    "docs/reference/security.md",
    "docs/reference/configuration.md",
    "docs/prompts/common.md",
    "docs/prompts/common-vi.md",
]


class DocumentationStructureTests(unittest.TestCase):
    def test_usage_information_architecture_exists(self):
        for relative in EXPECTED_DOCS:
            with self.subTest(relative=relative):
                self.assertTrue((ROOT / relative).is_file())

    def test_primary_navigation_has_no_broken_relative_links(self):
        sources = [
            "README.md",
            "README_vi.md",
            "docs/usage.md",
            "docs/usage-vi.md",
            "docs/pr-task-contract.md",
        ]
        pattern = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
        for relative in sources:
            source = ROOT / relative
            text = source.read_text(encoding="utf-8")
            for target in pattern.findall(text):
                if target.startswith(("http://", "https://", "#")):
                    continue
                path = target.split("#", 1)[0]
                if not path:
                    continue
                resolved = (source.parent / path).resolve()
                with self.subTest(source=relative, target=target):
                    self.assertTrue(resolved.exists())

    def test_usage_pages_are_routers_not_monolithic_handbooks(self):
        english = (ROOT / "docs/usage.md").read_text(encoding="utf-8")
        vietnamese = (ROOT / "docs/usage-vi.md").read_text(encoding="utf-8")
        for text in (english, vietnamese):
            self.assertIn("workflows/bug-fix.md", text)
            self.assertIn("operations/ci-failure.md", text)
            self.assertIn("reference/task-manifest.md", text)
            self.assertIn("prompts/common", text)
            self.assertLess(len(text.splitlines()), 120)


if __name__ == "__main__":
    unittest.main()
