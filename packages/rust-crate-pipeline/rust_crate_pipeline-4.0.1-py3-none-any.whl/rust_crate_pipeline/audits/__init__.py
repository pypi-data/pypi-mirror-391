"""Audit utilities for :mod:`rust_crate_pipeline`.

The audits helpers were previously treated as loose scripts and required
callers to modify ``sys.path`` before importing them.  Exposing
``calculate_db_hash`` here makes it straightforward to consume the audit logic
through package-relative imports.
"""

from .validate_db_hash import calculate_db_hash

__all__ = ["calculate_db_hash"]
