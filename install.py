from __future__ import annotations

import argparse
import json
import os
import shutil
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
TEMPLATE_ROOT = ROOT / "templates" / "project"

FILES = (
    (Path(".vibe/config.json"), Path(".vibe/config.json")),
    (Path(".vibe/project-context.json"), Path(".vibe/project-context.json")),
    (Path(".vibe/README.md"), Path(".vibe/README.md")),
)

SKIP_DIRS = {
    ".git", ".vibe", "node_modules", "vendor", ".venv", "venv",
    "dist", "build", "coverage", ".next", ".nuxt", "target",
}


def _read(path: Path, limit: int = 100_000) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")[:limit]
    except OSError:
        return ""


def _iter_files(target: Path, limit: int = 500) -> list[Path]:
    result: list[Path] = []
    for current, dirs, files in os.walk(target):
        dirs[:] = sorted(d for d in dirs if d not in SKIP_DIRS)
        for filename in sorted(files):
            path = Path(current) / filename
            result.append(path)
            if len(result) >= limit:
                return result
    return result


def _package_json(target: Path) -> dict[str, Any]:
    path = target / "package.json"
    if not path.exists():
        return {}
    try:
        value = json.loads(_read(path))
        return value if isinstance(value, dict) else {}
    except json.JSONDecodeError:
        return {}


def detect_project_context(target: Path) -> dict[str, Any]:
    target = target.resolve()
    files = _iter_files(target)
    rels = {path.relative_to(target).as_posix(): path for path in files}
    suffixes = {path.suffix.lower() for path in files}

    languages: list[str] = []
    if ".py" in suffixes or "pyproject.toml" in rels or "requirements.txt" in rels:
        languages.append("python")
    if ".ts" in suffixes or ".tsx" in suffixes or "tsconfig.json" in rels:
        languages.append("typescript")
    if ".js" in suffixes or ".jsx" in suffixes or "package.json" in rels:
        languages.append("javascript")
    if ".rb" in suffixes or "Gemfile" in rels:
        languages.append("ruby")
    if ".php" in suffixes or "composer.json" in rels:
        languages.append("php")
    if ".go" in suffixes or "go.mod" in rels:
        languages.append("go")
    if ".rs" in suffixes or "Cargo.toml" in rels:
        languages.append("rust")
    if ".java" in suffixes or "pom.xml" in rels or "build.gradle" in rels or "build.gradle.kts" in rels:
        languages.append("java")

    manifest_text = "\n".join(
        _read(target / name).lower()
        for name in (
            "pyproject.toml", "requirements.txt", "requirements-dev.txt",
            "Gemfile", "composer.json", "package.json",
        )
        if (target / name).exists()
    )
    package = _package_json(target)
    deps: dict[str, Any] = {}
    for key in ("dependencies", "devDependencies", "peerDependencies"):
        value = package.get(key)
        if isinstance(value, dict):
            deps.update(value)

    frameworks: list[str] = []

    def add_framework(name: str) -> None:
        if name not in frameworks:
            frameworks.append(name)

    if "fastapi" in manifest_text:
        add_framework("fastapi")
    if "django" in manifest_text or "manage.py" in rels:
        add_framework("django")
    if "flask" in manifest_text:
        add_framework("flask")
    if "rails" in manifest_text and "ruby" in languages:
        add_framework("rails")
    if "laravel" in manifest_text:
        add_framework("laravel")

    dep_names = set(deps)
    if "next" in dep_names:
        add_framework("nextjs")
    if "react" in dep_names:
        add_framework("react")
    if "vue" in dep_names:
        add_framework("vue")
    if "nuxt" in dep_names:
        add_framework("nuxt")
    if "svelte" in dep_names:
        add_framework("svelte")
    if "@sveltejs/kit" in dep_names:
        add_framework("sveltekit")
    if "vite" in dep_names:
        add_framework("vite")
    if "express" in dep_names:
        add_framework("express")
    if "@nestjs/core" in dep_names:
        add_framework("nestjs")

    theme_style = target / "style.css"
    functions_php = target / "functions.php"
    if functions_php.exists() and "theme name:" in _read(theme_style).lower():
        add_framework("wordpress")
    if any("/wp-content/themes/" in f"/{rel}/" for rel in rels):
        add_framework("wordpress")

    entrypoints: list[str] = []
    common_entrypoints = (
        "app/main.py", "main.py", "manage.py",
        "src/main.ts", "src/main.js", "src/index.ts", "src/index.js",
        "app/page.tsx", "app/page.jsx", "pages/index.tsx", "pages/index.jsx",
        "config/routes.rb", "config.ru", "functions.php",
        "cmd/main.go", "src/main.rs",
    )
    for path in common_entrypoints:
        if path in rels and path not in entrypoints:
            entrypoints.append(path)

    verification: list[str] = []
    scripts = package.get("scripts", {}) if isinstance(package.get("scripts"), dict) else {}

    package_manager = "npm"
    declared_manager = package.get("packageManager")
    if isinstance(declared_manager, str):
        candidate = declared_manager.split("@", 1)[0].strip().lower()
        if candidate in {"npm", "pnpm", "yarn", "bun"}:
            package_manager = candidate
    elif "pnpm-lock.yaml" in rels:
        package_manager = "pnpm"
    elif "yarn.lock" in rels:
        package_manager = "yarn"
    elif "bun.lock" in rels or "bun.lockb" in rels:
        package_manager = "bun"

    def package_script_command(script: str) -> str:
        if package_manager == "npm":
            return "npm test" if script == "test" else f"npm run {script}"
        if package_manager == "bun":
            return f"bun run {script}"
        return f"{package_manager} {script}"

    for script in ("test", "lint", "typecheck", "build"):
        if script in scripts:
            command = package_script_command(script)
            if command not in verification:
                verification.append(command)

    if "python" in languages:
        pytest_configured = (
            "pytest" in manifest_text
            or "[tool.pytest" in manifest_text
            or "pytest.ini" in rels
            or "tox.ini" in rels and "pytest" in _read(target / "tox.ini").lower()
        )
        has_python_tests = any(
            rel.startswith("tests/") and Path(rel).name.startswith("test") and rel.endswith(".py")
            for rel in rels
        )
        if pytest_configured:
            verification.append("pytest")
        elif "manage.py" in rels:
            verification.append("python manage.py test")
        elif has_python_tests:
            verification.append("python -m unittest discover")
        if "ruff" in manifest_text:
            verification.append("ruff check .")
        if "mypy" in manifest_text:
            verification.append("mypy .")
        elif "pyright" in manifest_text:
            verification.append("pyright")

    if "rails" in frameworks:
        if any(rel.startswith("spec/") for rel in rels):
            verification.append("bundle exec rspec")
        else:
            verification.append("bundle exec rails test")
    if "go" in languages:
        verification.append("go test ./...")
    if "rust" in languages:
        verification.append("cargo test")
    if "java" in languages:
        if "gradlew" in rels or "gradlew.bat" in rels:
            verification.append("./gradlew test")
        elif "pom.xml" in rels:
            verification.append("mvn test")
    if "php" in languages and ("phpunit.xml" in rels or "phpunit.xml.dist" in rels):
        verification.append("vendor/bin/phpunit")

    verification = list(dict.fromkeys(verification))

    project_name = package.get("name") if isinstance(package.get("name"), str) else target.name
    return {
        "schema_version": 1,
        "project": {
            "name": project_name,
            "summary": None,
        },
        "languages": languages,
        "primary_language": languages[0] if languages else None,
        "frameworks": frameworks,
        "entrypoints": entrypoints[:8],
        "verification": {
            "commands": verification[:8],
        },
        "context_limits": {
            "max_dependency_depth": 2,
            "max_source_files": 15,
            "max_test_files": 6,
            "max_related_modules": 6,
        },
        "dependency_authority": {
            "level": "advisory",
            "model": "static-best-effort",
        },
    }


def install(target: Path, *, dry_run: bool = False, force: bool = False) -> list[str]:
    target = target.resolve()
    actions: list[str] = []
    wrote_project_context = False

    for source_rel, target_rel in FILES:
        source = TEMPLATE_ROOT / source_rel
        destination = target / target_rel
        if destination.exists() and not force:
            actions.append(f"preserve {target_rel.as_posix()}")
            continue
        actions.append(f"write {target_rel.as_posix()}")
        if target_rel == Path(".vibe/project-context.json"):
            wrote_project_context = True
        if not dry_run:
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, destination)

    agents_source = TEMPLATE_ROOT / "AGENTS.md"
    agents_destination = target / "AGENTS.md"
    if agents_destination.exists():
        actions.append("preserve AGENTS.md")
    else:
        actions.append("write AGENTS.md")
        if not dry_run:
            shutil.copyfile(agents_source, agents_destination)

    if wrote_project_context:
        actions.append("detect project context")
        if not dry_run:
            detected = detect_project_context(target)
            (target / ".vibe/project-context.json").write_text(
                json.dumps(detected, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )

    return actions


def main() -> int:
    parser = argparse.ArgumentParser(description="Install the gpt-web-vibe-kit project contract.")
    parser.add_argument("--target", required=True, type=Path)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    for action in install(args.target, dry_run=args.dry_run, force=args.force):
        print(action)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
