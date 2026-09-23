import unittest
from pathlib import Path

from install import detect_project_context
from runtime.retrieval import extract_symbols, iterative_retrieve, query_tokens

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests" / "fixtures"

class RetrievalTests(unittest.TestCase):
    def test_query_tokens_split_identifiers(self):
        tokens = query_tokens("Fix refreshToken after expired session"); self.assertIn("refresh", tokens); self.assertIn("token", tokens); self.assertIn("expired", tokens)

    def test_extract_symbols_multiple_languages(self):
        symbols = extract_symbols("def refresh_access_token():\n    pass\nexport function rotateSessionCookie() {}\nclass SessionRefresher\nend\n")
        self.assertIn("refresh_access_token", symbols); self.assertIn("rotateSessionCookie", symbols); self.assertIn("SessionRefresher", symbols)

    def test_fastapi_iterative_retrieval_finds_target_consumer_and_test(self):
        paths = iterative_retrieve(FIXTURES / "fastapi-small", "Fix refresh token after session expiry", max_files=8)
        self.assertIn("app/services/auth_service.py", paths); self.assertIn("tests/test_auth.py", paths); self.assertIn("app/main.py", paths)

    def test_nextjs_iterative_retrieval_finds_session_symbol_neighborhood(self):
        paths = iterative_retrieve(FIXTURES / "nextjs-small", "Fix session cookie rotation after an expired session", max_files=8)
        self.assertIn("lib/session.ts", paths); self.assertIn("app/api/session/route.ts", paths); self.assertIn("tests/session.test.ts", paths)

    def test_rails_iterative_retrieval_finds_service_and_consumer(self):
        paths = iterative_retrieve(FIXTURES / "rails-small", "Fix session refresh after expiry", max_files=8)
        self.assertIn("app/services/session_refresher.rb", paths); self.assertIn("app/controllers/sessions_controller.rb", paths); self.assertIn("test/services/session_refresher_test.rb", paths)

    def test_fastapi_bootstrap_detection(self):
        context = detect_project_context(FIXTURES / "fastapi-small"); self.assertEqual(context["primary_language"], "python"); self.assertIn("fastapi", context["frameworks"]); self.assertIn("pytest", context["verification"]["commands"])

    def test_nextjs_bootstrap_detection(self):
        context = detect_project_context(FIXTURES / "nextjs-small"); self.assertIn("typescript", context["languages"]); self.assertIn("nextjs", context["frameworks"]); self.assertIn("npm test", context["verification"]["commands"]); self.assertIn("npm run build", context["verification"]["commands"])

    def test_rails_bootstrap_detection(self):
        context = detect_project_context(FIXTURES / "rails-small"); self.assertIn("ruby", context["languages"]); self.assertIn("rails", context["frameworks"]); self.assertIn("bundle exec rails test", context["verification"]["commands"])

if __name__ == "__main__": unittest.main()
