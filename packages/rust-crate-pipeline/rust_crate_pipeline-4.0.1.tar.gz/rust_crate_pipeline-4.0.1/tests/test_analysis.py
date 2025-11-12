"""Tests for the analysis module."""

import io
import logging
import os
import tarfile
from unittest.mock import Mock, patch

import requests

from rust_crate_pipeline.analysis import (
    DependencyAnalyzer,
    RustCodeAnalyzer,
    SecurityAnalyzer,
    SourceAnalyzer,
    UserBehaviorAnalyzer,
)
from rust_crate_pipeline.config import EnrichedCrate


class TestRustCodeAnalyzer:
    """Test RustCodeAnalyzer helper functions."""

    def test_create_and_aggregate(self, sample_rust_code):
        """Ensure metrics aggregation works with structure detection."""
        metrics = RustCodeAnalyzer.create_empty_metrics()
        analysis = RustCodeAnalyzer.analyze_rust_content(sample_rust_code)
        structure = RustCodeAnalyzer.detect_project_structure(
            [
                "src/lib.rs",
                "tests/test.rs",
                "examples/demo.rs",
                "benches/bench.rs",
            ]
        )
        result = RustCodeAnalyzer.aggregate_metrics(metrics, analysis, structure)

        assert result["loc"] > 0
        assert "test_method" in result["functions"]
        assert result["has_tests"] is True
        assert result["has_examples"] is True
        assert result["has_benchmarks"] is True

    def test_detect_project_structure(self):
        """Validate structure detection flags."""
        files = [
            "src/main.rs",
            "tests/test.rs",
            "examples/demo.rs",
            "benches/bench.rs",
        ]
        structure = RustCodeAnalyzer.detect_project_structure(files)

        assert structure["has_tests"] is True
        assert structure["has_examples"] is True
        assert structure["has_benchmarks"] is True


class TestSourceAnalyzer:
    """Test SourceAnalyzer class."""

    def test_analyze_crate_source_no_repo(self, sample_crate):
        """Test source analysis with no repository."""
        sample_crate.repository = ""
        result = SourceAnalyzer.analyze_crate_source(sample_crate)

        assert "error" in result
        assert "attempted_sources" in result
        assert result["file_count"] == 0
        assert result["loc"] == 0

    @patch("rust_crate_pipeline.analysis.get_with_retry")
    def test_analyze_crate_source_crates_io_success(self, mock_get, sample_crate):
        """Test successful crates.io analysis."""
        # Mock successful response
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None

        # Create a simple tar.gz content
        tar_content = io.BytesIO()
        with tarfile.open(fileobj=tar_content, mode="w:gz") as tar:
            # Add a dummy file
            info = tarfile.TarInfo("test.rs")
            info.size = len(b"fn test() {}")
            tar.addfile(info, io.BytesIO(b"fn test() {}"))

        mock_response.content = tar_content.getvalue()
        mock_get.return_value = mock_response

        result = SourceAnalyzer.analyze_crate_source(sample_crate)

        assert "error" not in result
        assert result["file_count"] == 1

    @patch("rust_crate_pipeline.analysis.SourceAnalyzer.analyze_crate_source_from_repo")
    @patch("rust_crate_pipeline.analysis.get_with_retry")
    def test_analyze_crate_source_crates_io_failure(
        self, mock_get, mock_analyze_repo, sample_crate, caplog
    ):
        """Test crates.io analysis failure."""
        # Mock the first request to fail, then fallback to GitHub which also fails
        mock_get.side_effect = requests.RequestException("Network error")
        mock_analyze_repo.return_value = {
            "error": "Failed to clone repository",
            "attempted_sources": ["git_clone"],
            "file_count": 0,
            "loc": 0,
        }

        with caplog.at_level(logging.WARNING):
            result = SourceAnalyzer.analyze_crate_source(sample_crate)

        assert "error" in result
        assert "attempted_sources" in result
        assert "Failed to download from crates.io" in caplog.text

    @patch("rust_crate_pipeline.analysis.get_with_retry")
    def test_analyze_crate_source_github_success(self, mock_get, sample_crate, caplog):
        """Test successful GitHub analysis."""
        # Mock crates.io failure, then GitHub success
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None

        # Create a simple tar.gz content
        tar_content = io.BytesIO()
        with tarfile.open(fileobj=tar_content, mode="w:gz") as tar:
            info = tarfile.TarInfo("test.rs")
            info.size = len(b"fn test() {}")
            tar.addfile(info, io.BytesIO(b"fn test() {}"))

        mock_response.content = tar_content.getvalue()
        mock_get.side_effect = [
            requests.RequestException("crates.io error"),
            mock_response,
        ]

        with caplog.at_level(logging.WARNING):
            result = SourceAnalyzer.analyze_crate_source(sample_crate)

        assert "error" not in result
        assert result["file_count"] == 1
        assert "Failed to download from crates.io" in caplog.text

    def test_analyze_local_directory(self, temp_dir, sample_rust_code):
        """Test local directory analysis."""
        # Create a src directory and add a Rust file
        src_dir = os.path.join(temp_dir, "src")
        os.makedirs(src_dir)

        rust_file = os.path.join(src_dir, "main.rs")
        with open(rust_file, "w") as f:
            f.write(sample_rust_code)

        # Create a Cargo.toml file
        cargo_file = os.path.join(temp_dir, "Cargo.toml")
        with open(cargo_file, "w") as f:
            f.write("[package]\nname = 'test'\nversion = '0.1.0'")

        result = SourceAnalyzer.analyze_local_directory(temp_dir)

        assert "error" not in result
        assert result["file_count"] == 1
        assert result["loc"] > 0

    def test_analyze_local_directory_no_rust_files(self, temp_dir):
        """Test local directory analysis with no Rust files."""
        # Create a directory with no Rust files
        with open(os.path.join(temp_dir, "README.md"), "w") as f:
            f.write("# Test")

        result = SourceAnalyzer.analyze_local_directory(temp_dir)

        assert result["file_count"] == 0
        assert len(result["functions"]) == 0

    def test_tarball_and_directory_consistency(self, temp_dir, sample_rust_code):
        """Ensure tarball and directory analyses yield same metrics."""
        # Create directory structure
        src_dir = os.path.join(temp_dir, "src")
        os.makedirs(src_dir)
        rust_file = os.path.join(src_dir, "lib.rs")
        with open(rust_file, "w") as f:
            f.write(sample_rust_code)

        # Build tarball from directory
        tar_bytes = io.BytesIO()
        with tarfile.open(fileobj=tar_bytes, mode="w:gz") as tar:
            tar.add(rust_file, arcname="crate/src/lib.rs")

        metrics_tar = SourceAnalyzer.analyze_crate_tarball(tar_bytes.getvalue())
        metrics_dir = SourceAnalyzer.analyze_local_directory(temp_dir)

        assert metrics_tar["loc"] == metrics_dir["loc"]
        assert metrics_tar["file_count"] == metrics_dir["file_count"]
        assert metrics_tar["functions"] == metrics_dir["functions"]


class TestSecurityAnalyzer:
    """Test SecurityAnalyzer class."""

    def test_check_security_metrics(self, sample_crate):
        """Test security metrics checking."""
        result = SecurityAnalyzer.check_security_metrics(sample_crate)

        assert isinstance(result, dict)
        assert "advisories" in result
        assert "vulnerability_count" in result
        assert "cargo_audit" in result
        assert "unsafe_blocks" in result


class TestUserBehaviorAnalyzer:
    """Test UserBehaviorAnalyzer class."""

    def test_get_github_headers_with_token(self, mock_github_token):
        """Test GitHub headers with token."""
        headers = UserBehaviorAnalyzer._get_github_headers()
        assert "Authorization" in headers
        assert headers["Authorization"] == "token test_token"

    def test_get_github_headers_without_token(self):
        """Test GitHub headers without token."""
        with patch.dict(os.environ, {}, clear=True):
            headers = UserBehaviorAnalyzer._get_github_headers()
            assert "Authorization" not in headers
            assert "Accept" in headers

    def test_fetch_user_behavior_data_no_github(self, sample_crate):
        """Test user behavior data fetching with no GitHub repo."""
        sample_crate.repository = "https://gitlab.com/test/test-crate"
        result = UserBehaviorAnalyzer.fetch_user_behavior_data(sample_crate)

        assert isinstance(result, dict)
        assert "issues" in result
        assert "pull_requests" in result
        assert "version_adoption" in result
        assert "community_metrics" in result

    @patch("requests.get")
    def test_fetch_user_behavior_data_github_success(self, mock_get, sample_crate):
        """Test successful GitHub user behavior data fetching."""
        # Mock GitHub API responses
        mock_issues_response = Mock()
        mock_issues_response.raise_for_status.return_value = None
        mock_issues_response.json.return_value = [
            {
                "number": 1,
                "title": "Test Issue",
                "state": "open",
                "created_at": "2023-01-01T00:00:00Z",
                "closed_at": None,
                "html_url": "https://github.com/test/test-crate/issues/1",
            }
        ]

        mock_activity_response = Mock()
        mock_activity_response.status_code = 200
        mock_activity_response.json.return_value = [{"total": 10}]

        mock_versions_response = Mock()
        mock_versions_response.raise_for_status.return_value = None
        mock_versions_response.json.return_value = {
            "versions": [
                {"num": "1.0.0", "downloads": 100, "created_at": "2023-01-01T00:00:00Z"}
            ]
        }

        mock_get.side_effect = [
            mock_issues_response,
            mock_activity_response,
            mock_versions_response,
        ]

        result = UserBehaviorAnalyzer.fetch_user_behavior_data(sample_crate)

        assert len(result["issues"]) == 1
        assert len(result["pull_requests"]) == 0
        assert "1.0.0" in result["version_adoption"]

    @patch("requests.get")
    def test_fetch_crates_io_versions_success(self, mock_get):
        """Test successful crates.io versions fetching."""
        # Mock crates.io API response
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "versions": [
                {
                    "num": "1.0.0",
                    "downloads": 100,
                    "created_at": "2023-01-01T00:00:00Z",
                },
                {"num": "0.9.0", "downloads": 50, "created_at": "2022-12-01T00:00:00Z"},
            ]
        }
        mock_get.return_value = mock_response

        result = {"version_adoption": {}}
        UserBehaviorAnalyzer._fetch_crates_io_versions("test-crate", result)

        assert "1.0.0" in result["version_adoption"]
        assert "0.9.0" in result["version_adoption"]
        assert result["version_adoption"]["1.0.0"]["downloads"] == 100


class TestDependencyAnalyzer:
    """Test DependencyAnalyzer class."""

    def test_analyze_dependencies(self, sample_crate):
        """Test dependency analysis."""
        # Create a second crate with dependencies
        crate2 = EnrichedCrate(
            name="crate2",
            version="1.0.0",
            description="Test crate 2",
            repository="",
            keywords=[],
            categories=[],
            readme="",
            downloads=0,
            github_stars=0,
            dependencies=[{"crate_id": "test-crate"}],
            features={},
            code_snippets=[],
            readme_sections={},
            librs_downloads=None,
            source="crates.io",
            enhanced_scraping={},
            enhanced_features=[],
            enhanced_dependencies=[],
            readme_summary="",
            feature_summary="",
            use_case="",
            score=0.0,
            factual_counterfactual="",
            source_analysis=None,
            user_behavior=None,
            security=None,
        )

        crates = [sample_crate, crate2]
        result = DependencyAnalyzer.analyze_dependencies(crates)

        assert "dependency_graph" in result
        assert "reverse_dependencies" in result
        assert "most_depended" in result
        assert "crate2" in result["dependency_graph"]
        assert "test-crate" in result["dependency_graph"]["crate2"]

    def test_analyze_dependencies_no_deps(self, sample_crate):
        """Test dependency analysis with no dependencies."""
        crates = [sample_crate]
        result = DependencyAnalyzer.analyze_dependencies(crates)

        assert "dependency_graph" in result
        assert "reverse_dependencies" in result
        assert "most_depended" in result
        assert result["dependency_graph"]["test-crate"] == []
