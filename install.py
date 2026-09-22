from __future__ import annotations

import argparse
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TEMPLATE_ROOT = ROOT / "templates" / "project"

FILES = (
    (Path(".vibe/config.json"), Path(".vibe/config.json")),
    (Path(".vibe/project-context.json"), Path(".vibe/project-context.json")),
    (Path(".vibe/README.md"), Path(".vibe/README.md")),
)


def install(target: Path, *, dry_run: bool = False, force: bool = False) -> list[str]:
    target = target.resolve()
    actions: list[str] = []
    for source_rel, target_rel in FILES:
        source = TEMPLATE_ROOT / source_rel
        destination = target / target_rel
        if destination.exists() and not force:
            actions.append(f"preserve {target_rel.as_posix()}")
            continue
        actions.append(f"write {target_rel.as_posix()}")
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
