from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Iterable, Mapping

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


def rank_candidates(
    files: Mapping[str, str],
    request: str,
    *,
    known_symbols: Iterable[str] = (),
) -> list[tuple[str, int]]:
    tokens = query_tokens(request)
    symbols = list(known_symbols)
    ranked: list[tuple[str, int]] = []
    for path, content in files.items():
        score = 0
        score += 3 * _text_score(path, tokens)
        score += 2 * _text_score(content, tokens)
        for symbol in symbols:
            if symbol and symbol in content:
                score += 8
            if symbol and symbol.lower() in path.lower():
                score += 4
        if score:
            ranked.append((path, score))
    return sorted(ranked, key=lambda item: (-item[1], item[0]))


def collect_project_files(root: Path, *, scan_limit: int = 500) -> dict[str, str]:
    result: dict[str, str] = {}
    count = 0
    for current, dirs, filenames in os.walk(root):
        dirs[:] = sorted(d for d in dirs if d not in SKIP_DIRS)
        for filename in sorted(filenames):
            path = Path(current) / filename
            if path.suffix.lower() not in CODE_SUFFIXES and filename not in {"Gemfile", "Dockerfile"}:
                continue
            rel = path.relative_to(root).as_posix()
            try:
                result[rel] = path.read_text(encoding="utf-8", errors="replace")[:100_000]
            except OSError:
                continue
            count += 1
            if count >= scan_limit:
                return result
    return result


def iterative_retrieve(
    root: Path,
    request: str,
    *,
    max_files: int = 15,
    max_rounds: int = 3,
    per_round: int = 5,
) -> list[str]:
    files = collect_project_files(root)
    request_tokens = set(query_tokens(request))
    selected: list[str] = []
    known_symbols: list[str] = []

    for _ in range(max_rounds):
        ranked = rank_candidates(files, request, known_symbols=known_symbols)
        additions = [path for path, _score in ranked if path not in selected][:per_round]
        if not additions:
            break
        selected.extend(additions)
        selected = selected[:max_files]

        discovered: list[str] = []
        for path in additions:
            for symbol in extract_symbols(files[path]):
                if _symbol_relevance(symbol, request_tokens) > 0 and symbol not in known_symbols:
                    discovered.append(symbol)
        known_symbols.extend(discovered[:20])
        if len(selected) >= max_files:
            break

    return selected
