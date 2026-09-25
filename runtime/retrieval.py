from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any, Iterable, Mapping

TOKEN_RE = re.compile(r"[A-Za-z][A-Za-z0-9_/-]{2,}")
IDENTIFIER_PART_RE = re.compile(r"[A-Z]?[a-z]+|[A-Z]+(?=[A-Z]|$)|[0-9]+")
SYMBOL_PATTERNS = [
    re.compile(r"(?m)^\s*(?:async\s+)?def\s+([A-Za-z_][A-Za-z0-9_]*)\s*\("),
    re.compile(r"(?m)^\s*class\s+([A-Za-z_][A-Za-z0-9_]*)\b"),
    re.compile(r"(?m)^\s*(?:export\s+)?(?:async\s+)?function\s+([A-Za-z_$][A-Za-z0-9_$]*)\s*\("),
    re.compile(r"(?m)^\s*(?:export\s+)?class\s+([A-Za-z_$][A-Za-z0-9_$]*)\b"),
    re.compile(r"(?m)^\s*(?:export\s+)?(?:interface|type)\s+([A-Za-z_$][A-Za-z0-9_$]*)\b"),
    re.compile(r"(?m)^\s*(?:export\s+)?(?:const|let|var)\s+([A-Za-z_$][A-Za-z0-9_$]*)\s*="),
    re.compile(r"(?m)^\s*(?:class|module)\s+([A-Za-z_][A-Za-z0-9_:]*)\b"),
    re.compile(r"(?m)^\s*def\s+([A-Za-z_][A-Za-z0-9_!?=]*)\b"),
    re.compile(r"(?m)^\s*(?:public\s+|private\s+|protected\s+)?function\s+([A-Za-z_][A-Za-z0-9_]*)\s*\("),
    re.compile(r"(?m)^\s*func\s+(?:\([^)]*\)\s*)?([A-Za-z_][A-Za-z0-9_]*)\s*\("),
    re.compile(r"(?m)^\s*(?:pub\s+)?fn\s+([A-Za-z_][A-Za-z0-9_]*)\s*\("),
]

STOPWORDS = {
    "add", "after", "all", "and", "bug", "build", "change", "code", "docs",
    "existing", "feature", "fix", "for", "from", "into", "issue", "make", "mode",
    "new", "only", "project", "refactor", "session", "should", "task", "test",
    "tests", "that", "the", "this", "when", "with", "without",
}

CODE_SUFFIXES = {
    ".py", ".js", ".jsx", ".ts", ".tsx", ".rb", ".php", ".go", ".rs", ".java",
    ".vue", ".svelte", ".astro", ".html", ".htm", ".css", ".scss", ".sass", ".less",
    ".json", ".yml", ".yaml", ".toml", ".ini", ".cfg", ".md",
}
SKIP_DIRS = {
    ".git", ".vibe", "node_modules", "vendor", ".venv", "venv", "dist", "build",
    "coverage", ".next", ".nuxt", "target",
}


def split_identifier(value: str) -> list[str]:
    value = value.replace("::", "_").replace("-", "_").replace("/", "_")
    parts: list[str] = []
    for chunk in value.split("_"):
        for part in IDENTIFIER_PART_RE.findall(chunk):
            item = part.lower()
            if len(item) >= 3 and item not in STOPWORDS:
                parts.append(item)
    return parts


def query_tokens(text: str) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for raw in TOKEN_RE.findall(text):
        for token in split_identifier(raw):
            if token not in seen:
                seen.add(token)
                result.append(token)
    return result


def extract_symbols(source: str) -> list[str]:
    seen: set[str] = set()
    symbols: list[str] = []
    for pattern in SYMBOL_PATTERNS:
        for match in pattern.finditer(source):
            symbol = match.group(1)
            if symbol not in seen:
                seen.add(symbol)
                symbols.append(symbol)
    return symbols


def _text_score(text: str, terms: Iterable[str]) -> int:
    lower = text.lower()
    score = 0
    for term in terms:
        if not term:
            continue
        count = lower.count(term.lower())
        if count:
            score += min(count, 5)
    return score


def _symbol_relevance(symbol: str, request_tokens: set[str]) -> int:
    parts = set(split_identifier(symbol))
    return len(parts & request_tokens)


def rank_candidates_diagnostics(
    files: Mapping[str, str],
    request: str,
    *,
    known_symbols: Iterable[str] = (),
) -> list[dict[str, Any]]:
    tokens = query_tokens(request)
    symbols = list(known_symbols)
    ranked: list[dict[str, Any]] = []
    for path, content in files.items():
        score = 0
        reasons: list[str] = []
        for token in tokens:
            path_hits = _text_score(path, (token,))
            content_hits = _text_score(content, (token,))
            if path_hits:
                score += 3 * path_hits
                reasons.append(f"path-token:{token}")
            if content_hits:
                score += 2 * content_hits
                reasons.append(f"content-token:{token}")
        for symbol in symbols:
            if symbol and symbol in content:
                score += 8
                reasons.append(f"symbol-content:{symbol}")
            if symbol and symbol.lower() in path.lower():
                score += 4
                reasons.append(f"symbol-path:{symbol}")
        if score:
            ranked.append({
                "path": path,
                "score": score,
                "reasons": list(dict.fromkeys(reasons)),
            })
    return sorted(ranked, key=lambda item: (-item["score"], item["path"]))


def rank_candidates(
    files: Mapping[str, str],
    request: str,
    *,
    known_symbols: Iterable[str] = (),
) -> list[tuple[str, int]]:
    return [
        (item["path"], item["score"])
        for item in rank_candidates_diagnostics(
            files,
            request,
            known_symbols=known_symbols,
        )
    ]


def collect_project_files(root: Path, *, scan_limit: int = 500) -> dict[str, str]:
    candidates: list[Path] = []
    for current, dirs, filenames in os.walk(root):
        dirs[:] = sorted(d for d in dirs if d not in SKIP_DIRS)
        for filename in sorted(filenames):
            path = Path(current) / filename
            if path.suffix.lower() not in CODE_SUFFIXES and filename not in {"Gemfile", "Dockerfile"}:
                continue
            candidates.append(path)

    # Select shallow paths first so an alphabetically early deep subtree cannot
    # consume the whole read budget before root-level entrypoints are considered.
    candidates.sort(
        key=lambda path: (
            len(path.relative_to(root).parts),
            path.relative_to(root).as_posix(),
        )
    )

    result: dict[str, str] = {}
    for path in candidates[:scan_limit]:
        rel = path.relative_to(root).as_posix()
        try:
            result[rel] = path.read_text(encoding="utf-8", errors="replace")[:100_000]
        except OSError:
            continue
    return result


def _configured_retrieval_limit(
    config: Mapping[str, Any] | None,
    key: str,
    default: int,
) -> int:
    if not isinstance(config, Mapping):
        return default
    context = config.get("context")
    if not isinstance(context, Mapping):
        return default
    value = context.get(key, default)
    return value if isinstance(value, int) and not isinstance(value, bool) else default


def iterative_retrieve_diagnostics(
    root: Path,
    request: str,
    *,
    config: Mapping[str, Any] | None = None,
    max_files: int = 15,
    max_rounds: int | None = None,
    per_round: int = 5,
    max_symbol_hints: int | None = None,
    scan_limit: int = 500,
) -> list[dict[str, Any]]:
    files = collect_project_files(root, scan_limit=scan_limit)
    request_tokens = set(query_tokens(request))
    rounds = (
        max_rounds
        if max_rounds is not None
        else _configured_retrieval_limit(config, "max_search_rounds", 3)
    )
    symbol_limit = (
        max_symbol_hints
        if max_symbol_hints is not None
        else _configured_retrieval_limit(config, "max_symbol_hints", 24)
    )

    selected_paths: list[str] = []
    selected: list[dict[str, Any]] = []
    known_symbols: list[str] = []

    for round_number in range(1, rounds + 1):
        ranked = rank_candidates_diagnostics(
            files,
            request,
            known_symbols=known_symbols,
        )
        additions = [
            item for item in ranked
            if item["path"] not in selected_paths
        ][:per_round]
        if not additions:
            break

        for item in additions:
            if len(selected_paths) >= max_files:
                break
            selected_paths.append(item["path"])
            selected.append({
                "path": item["path"],
                "score": item["score"],
                "round": round_number,
                "reasons": item["reasons"],
            })

        discovered: list[str] = []
        for item in additions:
            path = item["path"]
            for symbol in extract_symbols(files[path]):
                if (
                    _symbol_relevance(symbol, request_tokens) > 0
                    and symbol not in known_symbols
                    and symbol not in discovered
                ):
                    discovered.append(symbol)
        remaining = max(0, symbol_limit - len(known_symbols))
        known_symbols.extend(discovered[:remaining])
        if len(selected_paths) >= max_files:
            break

    return selected


def iterative_retrieve(
    root: Path,
    request: str,
    *,
    config: Mapping[str, Any] | None = None,
    max_files: int = 15,
    max_rounds: int | None = None,
    per_round: int = 5,
    max_symbol_hints: int | None = None,
    scan_limit: int = 500,
) -> list[str]:
    return [
        item["path"]
        for item in iterative_retrieve_diagnostics(
            root,
            request,
            config=config,
            max_files=max_files,
            max_rounds=max_rounds,
            per_round=per_round,
            max_symbol_hints=max_symbol_hints,
            scan_limit=scan_limit,
        )
    ]
