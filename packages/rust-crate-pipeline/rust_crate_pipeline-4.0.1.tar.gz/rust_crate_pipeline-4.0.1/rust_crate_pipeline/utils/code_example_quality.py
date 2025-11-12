"""Utilities for assessing Rust code example quality heuristics."""
from __future__ import annotations

from rust_crate_pipeline.quality.heuristics import get_quality_checker

__all__ = ["is_high_quality_example"]


def is_high_quality_example(code: str, crate_name: str = "", *, use_legacy: bool = False) -> bool:
    """Return ``True`` if the Rust ``code`` snippet appears to be high quality."""

    checker = get_quality_checker(use_legacy)
    return checker(code)
