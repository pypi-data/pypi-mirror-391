"""Input validation utilities for the Rust Crate Pipeline.

Provides validation functions for crate names, URLs, and other inputs
to prevent security issues and ensure data integrity.
"""

import re
from urllib.parse import urlparse

from ..exceptions import ConfigurationError, ValidationError as PipelineValidationError

# Rust crate name pattern: lowercase alphanumeric, hyphens, underscores
# Must start with a letter or number
CRATE_NAME_PATTERN = re.compile(r"^[a-z0-9][a-z0-9_-]*$")

# Maximum crate name length (crates.io limit)
MAX_CRATE_NAME_LENGTH = 64

# Semantic versioning pattern for crate versions
# Allows: MAJOR.MINOR.PATCH[-PRERELEASE][+BUILD]
# Prohibits path traversal characters: /, \, .., and other dangerous chars
# Based on SemVer 2.0.0 spec: https://semver.org/
CRATE_VERSION_PATTERN = re.compile(
    r"^[0-9]+\.[0-9]+\.[0-9]+(-[0-9A-Za-z\-\.]+)?(\+[0-9A-Za-z\-\.]+)?$"
)

# Maximum version string length (reasonable limit)
MAX_VERSION_LENGTH = 128


def validate_crate_name(crate_name: str) -> str:
    """Validate a Rust crate name.

    Args:
        crate_name: The crate name to validate

    Returns:
        The validated crate name (normalized to lowercase)

    Raises:
        PipelineValidationError: If the crate name is invalid
    """
    if not isinstance(crate_name, str):
        raise PipelineValidationError(
            f"Crate name must be a string, got {type(crate_name).__name__}"
        )

    crate_name = crate_name.strip().lower()

    if not crate_name:
        raise PipelineValidationError("Crate name cannot be empty")

    if len(crate_name) > MAX_CRATE_NAME_LENGTH:
        raise PipelineValidationError(
            f"Crate name exceeds maximum length of {MAX_CRATE_NAME_LENGTH} characters"
        )

    if not CRATE_NAME_PATTERN.match(crate_name):
        raise PipelineValidationError(
            f"Invalid crate name '{crate_name}': "
            "must contain only lowercase letters, numbers, hyphens, and underscores, "
            "and must start with a letter or number"
        )

    return crate_name


def validate_url(url: str, allowed_schemes: tuple[str, ...] = ("http", "https")) -> str:
    """Validate a URL.

    Args:
        url: The URL to validate
        allowed_schemes: Tuple of allowed URL schemes (default: http, https)

    Returns:
        The validated URL

    Raises:
        PipelineValidationError: If the URL is invalid
    """
    if not isinstance(url, str):
        raise PipelineValidationError(
            f"URL must be a string, got {type(url).__name__}"
        )

    url = url.strip()

    if not url:
        raise PipelineValidationError("URL cannot be empty")

    try:
        parsed = urlparse(url)
    except Exception as e:
        raise PipelineValidationError(f"Invalid URL format: {e}") from e

    if not parsed.scheme:
        raise PipelineValidationError(f"URL missing scheme: {url}")

    if parsed.scheme not in allowed_schemes:
        raise PipelineValidationError(
            f"URL scheme '{parsed.scheme}' not allowed. "
            f"Allowed schemes: {', '.join(allowed_schemes)}"
        )

    if not parsed.netloc:
        raise PipelineValidationError(f"URL missing netloc (domain): {url}")

    return url


def sanitize_crate_name_for_command(crate_name: str) -> str:
    """Sanitize a crate name for use in shell commands.

    This function validates the crate name and returns it in a safe format.
    For additional safety, use shlex.quote() when constructing commands.

    Args:
        crate_name: The crate name to sanitize

    Returns:
        The sanitized crate name

    Raises:
        PipelineValidationError: If the crate name is invalid
    """
    validated = validate_crate_name(crate_name)
    # Additional sanitization: ensure no shell metacharacters
    if any(char in validated for char in [";", "&", "|", "`", "$", "(", ")", "<", ">"]):
        raise PipelineValidationError(
            f"Crate name contains invalid characters: {crate_name}"
        )
    return validated


def validate_crate_version(crate_version: str) -> str:
    """Validate a Rust crate version string.

    Validates that the version follows semantic versioning format and does not
    contain path traversal characters or other dangerous patterns.

    Args:
        crate_version: The version string to validate

    Returns:
        The validated version string

    Raises:
        PipelineValidationError: If the version is invalid

    Examples:
        >>> validate_crate_version("1.2.3")
        '1.2.3'
        >>> validate_crate_version("1.0.0-alpha.1")
        '1.0.0-alpha.1'
        >>> validate_crate_version("2.0.0+build.1")
        '2.0.0+build.1'
    """
    if not isinstance(crate_version, str):
        raise PipelineValidationError(
            f"Crate version must be a string, got {type(crate_version).__name__}"
        )

    crate_version = crate_version.strip()

    if not crate_version:
        raise PipelineValidationError("Crate version cannot be empty")

    if len(crate_version) > MAX_VERSION_LENGTH:
        raise PipelineValidationError(
            f"Crate version exceeds maximum length of {MAX_VERSION_LENGTH} characters"
        )

    # Check for path traversal patterns
    dangerous_patterns = ["..", "/", "\\", "\x00"]
    for pattern in dangerous_patterns:
        if pattern in crate_version:
            raise PipelineValidationError(
                f"Invalid crate version '{crate_version}': "
                f"contains dangerous pattern '{pattern}'"
            )

    # Validate against semver pattern
    if not CRATE_VERSION_PATTERN.match(crate_version):
        raise PipelineValidationError(
            f"Invalid crate version '{crate_version}': "
            "must follow semantic versioning format (MAJOR.MINOR.PATCH[-PRERELEASE][+BUILD])"
        )

    return crate_version

