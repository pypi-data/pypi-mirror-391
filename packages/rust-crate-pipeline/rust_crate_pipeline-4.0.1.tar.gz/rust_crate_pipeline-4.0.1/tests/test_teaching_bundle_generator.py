import json
from datetime import datetime
from pathlib import Path

import pytest

from generate_teaching_bundles import TeachingBundleGenerator


TEST_PIPELINE_CONFIG = {
    "pipeline_version": "9.9.9",
    "schema_version": "2024-06",
    "dataset_id": "unit-test-dataset",
    "git_commit": "deadbeef1234567890",
    "teaching_bundle_output_dir": "./teaching_bundles",
    "instruction_llm": {"enabled": False},
}


def build_analysis(crate_name: str, license_snippet: str) -> dict:
    return {
        "input_data": crate_name,
        "audit_info": {
            "sanitized_documentation": {
                "crates_io": {
                    "content": license_snippet,
                    "error": None,
                    "status_code": 200,
                }
            },
            "crate_analysis": {
                "enhanced_analysis": {
                    "insights": {
                        "clippy_insights": {"warning_count": 0, "error_count": 0},
                        "geiger_insights": {"total_unsafe_items": 0},
                        "audit_insights": {"vulnerability_count": 0},
                        "dependency_health": {"health_score": 1.0},
                        "overall_quality_score": 0.9,
                        "security_risk_level": "low",
                        "maintenance_health": "healthy",
                        "performance_indicators": {
                            "documentation_quality": "excellent",
                            "complexity_estimate": 2,
                        },
                    },
                    "build": {"returncode": 0},
                    "test": {"returncode": 0},
                    "environment": {
                        "has_tests": True,
                        "features": ["default"],
                        "rust_version": "1.70",
                        "version": "1.2.3",
                    },
                }
            },
        },
    }


@pytest.fixture
def tmp_analysis_path(tmp_path: Path):
    def _writer(crate_name: str, license_snippet: str) -> Path:
        analysis = build_analysis(crate_name, license_snippet)
        path = tmp_path / f"{crate_name}_analysis.json"
        path.write_text(json.dumps(analysis), encoding="utf-8")
        return path

    return _writer


def test_generate_bundle_records_license_metadata(tmp_path: Path, monkeypatch, tmp_analysis_path):
    crate_name = "permissive_crate"
    license_text = (
        "## Metadata\n"
        "[ MIT ](https://choosealicense.com/licenses/mit) OR "
        "[ Apache-2.0 ](https://choosealicense.com/licenses/apache-2.0)\n"
    )
    analysis_file = tmp_analysis_path(crate_name, license_text)

    generator = TeachingBundleGenerator(
        output_dir=tmp_path, pipeline_config=TEST_PIPELINE_CONFIG
    )

    def fake_metadata(self, name):
        assert name == crate_name
        return {"crate": {"max_version": "1.2.3", "license": "MIT OR Apache-2.0"}}

    def fake_blocks(self, content):
        return [("docs_example", "pub fn demo() {}")]

    def fake_deps(self, code, name):
        return []

    def fake_versions(self, crate, deps):
        return {crate: "1.2.3"}

    def fake_formatter(self, crate_name, crate_version, code, dep_versions, features):
        return code

    def fake_tests(self, code, topic):
        return ["#[test] fn it_works() { assert_eq!(2 + 2, 4); }"]

    def fake_download(self, crate_name, version=None, crate_data=None):
        return None

    def fake_run(self, cmd, cwd):
        return 0

    monkeypatch.setattr(TeachingBundleGenerator, "_fetch_crate_api_metadata", fake_metadata)
    monkeypatch.setattr(TeachingBundleGenerator, "extract_rust_code_blocks", fake_blocks)
    monkeypatch.setattr(TeachingBundleGenerator, "extract_dependencies_from_code", fake_deps)
    monkeypatch.setattr(TeachingBundleGenerator, "_resolve_dependency_versions", fake_versions)
    monkeypatch.setattr(TeachingBundleGenerator, "_format_and_check_example", fake_formatter)
    monkeypatch.setattr(TeachingBundleGenerator, "generate_tests_for_code", fake_tests)
    monkeypatch.setattr(TeachingBundleGenerator, "download_crate_source", fake_download)
    monkeypatch.setattr(TeachingBundleGenerator, "_run_cargo_command", fake_run)

    result = generator.generate_bundle_for_crate(analysis_file)
    assert result is True

    quality_path = tmp_path / crate_name / "quality_labels.json"
    assert quality_path.exists()

    data = json.loads(quality_path.read_text(encoding="utf-8"))
    labels = data["quality_labels"]
    metadata = data["metadata"]

    assert sorted(labels["detected_licenses"]) == ["Apache-2.0", "MIT"]
    assert labels["license_status"] == "allowed"
    assert labels["license_allowed"] is True
    assert "licenses" in labels["license_message"].lower()

    assert metadata["pipeline_version"] == TEST_PIPELINE_CONFIG["pipeline_version"]
    assert metadata["schema_version"] == TEST_PIPELINE_CONFIG["schema_version"]
    assert metadata["dataset_id"] == TEST_PIPELINE_CONFIG["dataset_id"]
    assert metadata["git_commit"] == TEST_PIPELINE_CONFIG["git_commit"]

    timestamp = metadata["generated_at"]
    # Replace Z with explicit offset for python's ISO parser
    parsed = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
    assert parsed.tzinfo is not None


def test_generate_bundle_skips_disallowed_license(tmp_path: Path, monkeypatch, tmp_analysis_path):
    crate_name = "forbidden_crate"
    license_text = "License: GPL-3.0-only"
    analysis_file = tmp_analysis_path(crate_name, license_text)

    generator = TeachingBundleGenerator(
        output_dir=tmp_path, pipeline_config=TEST_PIPELINE_CONFIG
    )

    def fake_metadata(self, name):
        assert name == crate_name
        return {"crate": {"max_version": "0.1.0", "license": "GPL-3.0"}}

    download_calls = {"count": 0}

    def fake_download(self, crate_name, version=None, crate_data=None):
        download_calls["count"] += 1
        return None

    monkeypatch.setattr(TeachingBundleGenerator, "_fetch_crate_api_metadata", fake_metadata)
    monkeypatch.setattr(TeachingBundleGenerator, "download_crate_source", fake_download)

    result = generator.generate_bundle_for_crate(analysis_file)

    assert result is False
    assert download_calls["count"] == 0
    assert not (tmp_path / crate_name).exists()
