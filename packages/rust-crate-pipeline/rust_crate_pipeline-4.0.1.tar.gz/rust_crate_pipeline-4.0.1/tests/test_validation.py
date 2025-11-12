"""Tests for input validation utilities."""

import pytest

from rust_crate_pipeline.exceptions import ValidationError as PipelineValidationError
from rust_crate_pipeline.utils.validation import (
    sanitize_crate_name_for_command,
    validate_crate_name,
    validate_crate_version,
    validate_url,
)


class TestValidateCrateName:
    """Test crate name validation."""

    def test_valid_crate_names(self):
        """Test that valid crate names pass validation."""
        valid_names = [
            "serde",
            "tokio",
            "test-crate",
            "test_crate",
            "test123",
            "a",
            "a-b-c",
            "a_b_c",
        ]
        for name in valid_names:
            result = validate_crate_name(name)
            assert result == name.lower().strip()

    def test_invalid_crate_names(self):
        """Test that invalid crate names raise ValidationError."""
        invalid_names = [
            "",
            "  ",
            "TestCrate",  # uppercase
            "test crate",  # space
            "test@crate",  # invalid character
            "test.crate",  # dot
            "test/crate",  # slash
            "test\\crate",  # backslash
            "test:crate",  # colon
            "A" * 65,  # too long
        ]
        for name in invalid_names:
            with pytest.raises(PipelineValidationError):
                validate_crate_name(name)

    def test_normalization(self):
        """Test that crate names are normalized to lowercase."""
        assert validate_crate_name("  SERDE  ") == "serde"
        assert validate_crate_name("Tokio") == "tokio"

    def test_non_string_input(self):
        """Test that non-string input raises ValidationError."""
        with pytest.raises(PipelineValidationError):
            validate_crate_name(123)
        with pytest.raises(PipelineValidationError):
            validate_crate_name(None)


class TestValidateURL:
    """Test URL validation."""

    def test_valid_urls(self):
        """Test that valid URLs pass validation."""
        valid_urls = [
            "http://example.com",
            "https://example.com",
            "https://example.com/path",
            "https://example.com:8080/path?query=value",
        ]
        for url in valid_urls:
            result = validate_url(url)
            assert result == url.strip()

    def test_invalid_urls(self):
        """Test that invalid URLs raise ValidationError."""
        invalid_urls = [
            "",
            "  ",
            "not-a-url",
            "ftp://example.com",  # wrong scheme
            "file:///etc/passwd",  # wrong scheme
            "javascript:alert(1)",  # wrong scheme
            "http://",  # missing netloc
            "https://",  # missing netloc
        ]
        for url in invalid_urls:
            with pytest.raises(PipelineValidationError):
                validate_url(url)

    def test_custom_allowed_schemes(self):
        """Test URL validation with custom allowed schemes."""
        assert validate_url("http://example.com", allowed_schemes=("http",)) == "http://example.com"
        with pytest.raises(PipelineValidationError):
            validate_url("https://example.com", allowed_schemes=("http",))

    def test_non_string_input(self):
        """Test that non-string input raises ValidationError."""
        with pytest.raises(PipelineValidationError):
            validate_url(123)
        with pytest.raises(PipelineValidationError):
            validate_url(None)


class TestSanitizeCrateNameForCommand:
    """Test crate name sanitization for command usage."""

    def test_valid_crate_names(self):
        """Test that valid crate names are sanitized correctly."""
        valid_names = ["serde", "tokio", "test-crate", "test_crate"]
        for name in valid_names:
            result = sanitize_crate_name_for_command(name)
            assert result == name.lower().strip()

    def test_invalid_crate_names(self):
        """Test that invalid crate names raise ValidationError."""
        invalid_names = [
            "test;rm -rf",
            "test&evil",
            "test|command",
            "test`backtick",
            "test$var",
            "test(evil)",
            "test<redirect",
            "test>redirect",
        ]
        for name in invalid_names:
            with pytest.raises(PipelineValidationError):
                sanitize_crate_name_for_command(name)

    def test_shell_metacharacters(self):
        """Test that shell metacharacters are rejected."""
        metacharacters = [";", "&", "|", "`", "$", "(", ")", "<", ">"]
        for char in metacharacters:
            with pytest.raises(PipelineValidationError):
                sanitize_crate_name_for_command(f"test{char}evil")


class TestValidateCrateVersion:
    """Test crate version validation."""

    def test_valid_versions(self):
        """Test that valid semver versions pass validation."""
        valid_versions = [
            "1.0.0",
            "0.1.0",
            "2.3.4",
            "10.20.30",
            "1.0.0-alpha",
            "1.0.0-alpha.1",
            "1.0.0-beta.2",
            "1.0.0-rc.1",
            "1.0.0+build.1",
            "1.0.0-alpha.1+build.1",
            "1.2.3-pre.4+build.5",
        ]
        for version in valid_versions:
            result = validate_crate_version(version)
            assert result == version.strip()

    def test_invalid_versions(self):
        """Test that invalid versions raise ValidationError."""
        invalid_versions = [
            "",
            "  ",
            "1.0",  # missing patch
            "1",  # incomplete
            "v1.0.0",  # prefix not allowed
            "1.0.0.0",  # too many components
            "1.0.0-",  # empty prerelease
            "1.0.0+",  # empty build
            "1.0.0-alpha/",  # path traversal
            "1.0.0-alpha\\",  # path traversal
            "1.0.0-../pwn",  # path traversal
            "1.0.0-\x00",  # null byte
            "1.0.0-alpha beta",  # space in prerelease
            "A" * 129,  # too long
        ]
        for version in invalid_versions:
            with pytest.raises(PipelineValidationError):
                validate_crate_version(version)

    def test_path_traversal_prevention(self):
        """Test that path traversal patterns are rejected."""
        traversal_patterns = [
            "../pwn",
            "..\\pwn",
            "1.0.0/../evil",
            "1.0.0\\..\\evil",
            "1.0.0-../test",
            "1.0.0+../test",
        ]
        for version in traversal_patterns:
            with pytest.raises(PipelineValidationError):
                validate_crate_version(version)

    def test_normalization(self):
        """Test that versions are normalized (trimmed)."""
        assert validate_crate_version("  1.0.0  ") == "1.0.0"

    def test_non_string_input(self):
        """Test that non-string input raises ValidationError."""
        with pytest.raises(PipelineValidationError):
            validate_crate_version(123)
        with pytest.raises(PipelineValidationError):
            validate_crate_version(None)

