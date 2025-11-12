"""Centralized heuristics for Rust snippet assessment."""
from __future__ import annotations

import math
import re
from dataclasses import dataclass
from typing import Callable, Final, List

# ---------------------------------------------------------------------------
# Shared constants
# ---------------------------------------------------------------------------

_MIN_CHARS: Final[int] = 50
_MAX_CHARS: Final[int] = 4000
_MIN_LINES: Final[int] = 3

_REQUIRED_CONSTRUCTS: Final[tuple[str, ...]] = (
    "fn ",
    "struct ",
    "enum ",
    "impl ",
    "trait ",
    "use ",
    "let ",
    "match ",
    "macro_rules!",
)

_ACCEPT_MARKERS: Final[tuple[str, ...]] = (
    "fn main",
    "async fn",
    "Result<",
    "Option<",
    "Vec<",
    "HashMap",
    "println!",
    "macro_rules!",
    "#[macro_export",
    "#[proc_macro",
    "async move",
    ".await",
    "tokio::",
)

_COMPLEXITY_FEATURES: Final[tuple[tuple[str, float], ...]] = (
    (r"fn\\s+\w+", 1.5),
    (r"impl\\s+\w+", 1.2),
    (r"trait\\s+\w+", 1.2),
    (r"enum\\s+\w+", 1.0),
    (r"struct\\s+\w+", 1.0),
    (r"match\\s+", 0.8),
    (r"async\\s", 1.0),
    (r"unsafe", 2.0),
    (r"<[^>]+>", 0.6),
    (r"::", 0.4),
    (r"for\\s+\\w+\\s+in", 0.6),
)

_TOPIC_RULES: Final[tuple[tuple[str, str], ...]] = (
    ("fn main", "main_function"),
    ("struct ", "data_structures"),
    ("enum ", "enumerations"),
    ("trait ", "traits"),
    ("async", "asynchronous_programming"),
    ("#[test]", "testing"),
    ("serde", "serialization"),
    ("tokio", "async_runtime"),
    ("std::", "standard_library"),
    ("Result<", "error_handling"),
    ("Error", "error_handling"),
    ("Iterator", "iterators"),
    ("Stream", "streams"),
)

_COMMENT_STARTERS: Final[tuple[str, ...]] = ("//", "/*")


@dataclass(frozen=True)
class _SnippetStats:
    """Pre-computed statistics for heuristics."""

    snippet: str
    stripped: str
    lines: List[str]

    @property
    def non_empty_lines(self) -> List[str]:
        return [line for line in self.lines if line.strip()]

    @property
    def line_count(self) -> int:
        return len(self.lines)


def _gather_stats(snippet: str) -> _SnippetStats:
    stripped = snippet.strip()
    lines = snippet.splitlines()
    return _SnippetStats(snippet=snippet, stripped=stripped, lines=lines)


def _balanced_pairs(snippet: str) -> bool:
    return snippet.count("{") == snippet.count("}") and snippet.count("(") == snippet.count(")")


def _has_required_construct(snippet: str) -> bool:
    return any(marker in snippet for marker in _REQUIRED_CONSTRUCTS)


def _has_accept_marker(snippet: str) -> bool:
    return any(marker in snippet for marker in _ACCEPT_MARKERS)


def _token_density(snippet: str) -> float:
    tokens = re.findall(r"[A-Za-z_][A-Za-z0-9_]*", snippet)
    if not tokens:
        return 0.0
    unique_tokens = len(set(tokens))
    length = max(len(snippet), 1)
    return unique_tokens / length


def _legacy_is_high_quality_snippet(snippet: str) -> bool:
    stats = _gather_stats(snippet)

    if len(snippet) < _MIN_CHARS or len(snippet) > _MAX_CHARS:
        return False

    if stats.stripped.startswith(_COMMENT_STARTERS):
        return False

    if not _balanced_pairs(snippet):
        return False

    if not _has_required_construct(snippet):
        return False

    if _has_accept_marker(snippet):
        return True

    if any(marker in stats.stripped for marker in ("macro_rules!", "#[macro_export", "#[proc_macro")):
        return True

    for prefix in ("struct ", "enum ", "trait "):
        if stats.stripped.startswith(prefix) or stats.stripped.startswith(f"pub {prefix}"):
            return True
        if stats.stripped.startswith("pub(crate) ") and stats.stripped[len("pub(crate) ") :].startswith(prefix):
            return True

    return False


def is_high_quality_snippet(snippet: str) -> bool:
    """Return ``True`` if the snippet appears to be a high-quality Rust example."""

    stats = _gather_stats(snippet)

    if len(stats.stripped) < _MIN_CHARS or len(stats.stripped) > _MAX_CHARS:
        return False

    if stats.line_count < _MIN_LINES or not stats.non_empty_lines:
        return False

    if stats.stripped.startswith(_COMMENT_STARTERS):
        return False

    if not _balanced_pairs(stats.snippet):
        return False

    if "todo!" in stats.snippet or "unimplemented!" in stats.snippet:
        return False

    if stats.non_empty_lines and any(line.strip().startswith("# ") for line in stats.lines[:2]):
        return False

    density = _token_density(stats.snippet)
    if density < 0.02:  # Too sparse, likely not real code
        return False

    if _has_accept_marker(stats.snippet):
        return True

    if _has_required_construct(stats.snippet):
        return True

    return _legacy_is_high_quality_snippet(stats.snippet)


def complexity_score(rs_code: str) -> float:
    """Return a normalized complexity score for the provided Rust code."""

    lines = [line for line in rs_code.splitlines() if line.strip()]
    line_score = min(len(lines) * 0.15, 6.0)

    feature_score = 0.0
    for pattern, weight in _COMPLEXITY_FEATURES:
        matches = re.findall(pattern, rs_code)
        feature_score += len(matches) * weight

    nesting_bonus = 0.0
    brace_depth = 0
    max_depth = 0
    for char in rs_code:
        if char == "{":
            brace_depth += 1
            max_depth = max(max_depth, brace_depth)
        elif char == "}":
            brace_depth = max(0, brace_depth - 1)
    if max_depth >= 4:
        nesting_bonus = 2.0
    elif max_depth == 3:
        nesting_bonus = 1.0

    raw_score = line_score + feature_score + nesting_bonus
    normalized = 1 - math.exp(-raw_score / 10.0)
    return min(max(normalized, 0.0), 1.0)


def detect_topics(rs_code: str) -> List[str]:
    """Detect high-level topics demonstrated by the Rust code."""

    lowered = rs_code.lower()
    topics: List[str] = []

    for marker, topic in _TOPIC_RULES:
        if marker.lower() in lowered:
            topics.append(topic)

    if re.search(r"#\[derive\s*\(.*serde::", lowered):
        if "serialization" not in topics:
            topics.append("serialization")

    if re.search(r"(Arc|Rc|Mutex|RwLock)(::|<)", rs_code):
        topics.append("concurrency")

    if "unsafe" in lowered:
        topics.append("unsafe_code")

    if "::from" in rs_code or "TryFrom" in rs_code:
        topics.append("conversions")

    if "Iterator" in rs_code and "collect" in rs_code:
        if "iterators" not in topics:
            topics.append("iterators")

    seen = set()
    ordered_topics = []
    for topic in topics:
        if topic not in seen:
            ordered_topics.append(topic)
            seen.add(topic)
    return ordered_topics


def get_quality_checker(use_legacy: bool) -> Callable[[str], bool]:
    """Return a quality checker respecting the legacy toggle."""

    return _legacy_is_high_quality_snippet if use_legacy else is_high_quality_snippet


__all__ = [
    "complexity_score",
    "detect_topics",
    "get_quality_checker",
    "is_high_quality_snippet",
]
