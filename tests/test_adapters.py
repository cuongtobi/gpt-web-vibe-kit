import json
import unittest
from pathlib import Path


class AdapterTests(unittest.TestCase):
    def test_all_adapter_files_are_valid_json_with_identity(self):
        root = Path(__file__).resolve().parents[1] / "adapters"
        files = sorted(root.glob("**/*.json"))
        self.assertTrue(files)
        for path in files:
            with self.subTest(path=str(path)):
                data = json.loads(path.read_text(encoding="utf-8"))
                self.assertIsInstance(data.get("id"), str)
                self.assertIn(data.get("kind"), {"language", "framework"})
                self.assertIsInstance(data.get("search"), dict)
                self.assertIsInstance(data.get("verification"), list)

    def test_frontend_adapter_metadata_is_lightweight(self):
        root = Path(__file__).resolve().parents[1] / "adapters" / "frameworks"
        for name in ("react", "nextjs", "vue", "nuxt", "svelte", "sveltekit"):
            with self.subTest(name=name):
                data = json.loads((root / f"{name}.json").read_text(encoding="utf-8"))
                self.assertIs(data.get("frontend"), True)
        vite = json.loads((root / "vite.json").read_text(encoding="utf-8"))
        self.assertIs(vite.get("frontend_tooling"), True)
        self.assertIsNone(vite.get("frontend"))

    def test_language_and_framework_parity_set(self):
        root = Path(__file__).resolve().parents[1] / "adapters"
        languages = {path.stem for path in (root / "languages").glob("*.json")}
        frameworks = {path.stem for path in (root / "frameworks").glob("*.json")}
        self.assertTrue({
            "generic", "python", "javascript", "typescript", "php",
            "ruby", "java", "go", "rust"
        }.issubset(languages))
        self.assertTrue({
            "flask", "fastapi", "django", "express", "nestjs", "react",
            "vue", "nuxt", "svelte", "sveltekit", "vite", "nextjs",
            "wordpress", "laravel", "rails", "spring", "gin", "fiber", "actix-web"
        }.issubset(frameworks))
