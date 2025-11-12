"""Compatibility utilities exposed as a top-level package.

This module re-exports the helpers that historically lived under
``rust_crate_pipeline.utils`` so that legacy imports such as
``import utils`` continue to function once the project is installed as a
package.  The ``rust_crate_pipeline`` package remains the canonical home
for these helpers, and the import here simply delegates to that module.

The star import is constrained by using ``__all__`` from the source module
to ensure only public APIs are exposed and to maintain namespace clarity.
"""

# Import all public symbols from rust_crate_pipeline.utils
# The star import is constrained by __all__ from the source module
from rust_crate_pipeline.utils import *  # noqa: F401,F403

# Explicitly constrain exports using __all__ from source module
try:  # pragma: no cover - falls back when ``__all__`` is absent.
    from rust_crate_pipeline.utils import __all__ as _ALL  # type: ignore[attr-defined]
    __all__ = list(_ALL)
except ImportError:  # pragma: no cover
    # Fallback: if __all__ is not available, export nothing explicitly
    # This prevents accidental exposure of private symbols
    __all__ = []
