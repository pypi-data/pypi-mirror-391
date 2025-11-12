"""Utility helpers for the :mod:`rust_crate_pipeline` package.

The helper modules historically lived as loose files that were imported by
mutating ``sys.path`` inside scripts.  Treating them as a proper subpackage
allows every consumer to rely on normal relative imports, which keeps the
package importable once it has been installed with ``pip install -e .``.
"""

from . import resume_utils, tagging, version_policy
from .advanced_cache import (AdvancedCache, CacheEntry, CacheMetrics,
                             CacheStrategy, DiskCache, MemoryCache, RedisCache,
                             get_cache)
from .code_example_quality import is_high_quality_example
from .file_utils import atomic_write_json
from .local_rag_manager import LocalRAGManager
from .logging_utils import configure_logging
from .rust_code_analyzer import RustCodeAnalyzer
from .serialization_utils import to_serializable
from .status_utils import ProgressTracker, status, with_retry
from .subprocess_utils import (cleanup_subprocess, run_command_with_cleanup,
                               setup_asyncio_windows_fixes)

# Export the high-level resume helpers directly so callers can simply import
# from :mod:`rust_crate_pipeline.utils` without reaching into submodules.
from .resume_utils import (create_resume_report, get_processed_crates,
                           get_remaining_crates, load_crate_list,
                           validate_resume_state)

__all__ = [
    # Cache helpers
    "AdvancedCache",
    "CacheEntry",
    "CacheMetrics",
    "CacheStrategy",
    "DiskCache",
    "MemoryCache",
    "RedisCache",
    "get_cache",
    # General utilities
    "atomic_write_json",
    "cleanup_subprocess",
    "configure_logging",
    "LocalRAGManager",
    "RustCodeAnalyzer",
    "is_high_quality_example",
    "run_command_with_cleanup",
    "setup_asyncio_windows_fixes",
    "status",
    "to_serializable",
    "with_retry",
    "ProgressTracker",
    # Resume utilities
    "create_resume_report",
    "get_processed_crates",
    "get_remaining_crates",
    "load_crate_list",
    "validate_resume_state",
    # Submodules that remain part of the public surface area
    "resume_utils",
    "tagging",
    "version_policy",
]
