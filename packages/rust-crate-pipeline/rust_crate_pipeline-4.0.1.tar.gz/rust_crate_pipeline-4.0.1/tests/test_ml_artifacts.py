"""Tests ensuring trained ML artifacts are managed correctly."""

from __future__ import annotations

import json
import pickle
from pathlib import Path

import pytest

from rust_crate_pipeline.ml.artifacts import (
    ARTIFACT_FILENAMES,
    LEGACY_METADATA_FILENAME,
    PROVENANCE_FILENAME,
    compute_artifact_hash,
    ensure_required_artifacts_exist,
    load_provenance,
)
from rust_crate_pipeline.ml.quality_predictor import CrateQualityPredictor


class _ArrayWrapper:
    def __init__(self, rows: int) -> None:
        self._rows = rows

    def toarray(self) -> list[list[float]]:
        return [[0.0] * 100 for _ in range(self._rows)]


class _StubRegressor:
    def __init__(self, value: float) -> None:
        self._value = value

    def predict(self, features: list[list[float]]) -> list[float]:
        return [self._value for _ in features]


class _StubClassifier:
    def __init__(self, label: int) -> None:
        self._label = label

    def predict(self, features: list[list[float]]) -> list[int]:
        return [self._label for _ in features]


class _StubVectorizer:
    def transform(self, texts: list[str]) -> _ArrayWrapper:
        return _ArrayWrapper(len(texts))


class _StubScaler:
    def transform(self, values):  # type: ignore[override]
        return values


def _write_stub_artifacts(model_dir: Path) -> dict[str, str]:
    """Create lightweight stand-ins for the trained artifacts used in tests."""

    model_dir.mkdir(parents=True, exist_ok=True)

    artifacts = {
        "quality_model.pkl": _StubRegressor(0.8),
        "security_model.pkl": _StubClassifier(1),
        "maintenance_model.pkl": _StubRegressor(0.7),
        "popularity_model.pkl": _StubClassifier(2),
        "dependency_model.pkl": _StubRegressor(0.6),
        "text_vectorizer.pkl": _StubVectorizer(),
        "feature_scaler.pkl": _StubScaler(),
    }

    for filename, artifact in artifacts.items():
        with (model_dir / filename).open("wb") as handle:
            pickle.dump(artifact, handle)

    feature_names = [f"feature_{index}" for index in range(114)]
    metadata = {"version": "test-version", "feature_names": feature_names}
    with (model_dir / LEGACY_METADATA_FILENAME).open("w", encoding="utf-8") as handle:
        json.dump(metadata, handle)

    artifact_hash = compute_artifact_hash(model_dir)
    provenance = {
        "version": metadata["version"],
        "artifact_hash": artifact_hash,
        "combined_feature_names": feature_names,
    }
    with (model_dir / PROVENANCE_FILENAME).open("w", encoding="utf-8") as handle:
        json.dump(provenance, handle)

    return {"artifact_hash": artifact_hash, "version": metadata["version"]}


def test_missing_artifacts_raise_helpful_error(tmp_path: Path) -> None:
    models_dir = tmp_path / "missing_models"
    models_dir.mkdir()

    with pytest.raises(FileNotFoundError) as exc:
        ensure_required_artifacts_exist(models_dir)

    assert "Run fix_ml_models.py" in str(exc.value)


def test_predictor_reports_missing_models(tmp_path: Path) -> None:
    predictor = CrateQualityPredictor(model_dir=str(tmp_path))

    with pytest.raises(RuntimeError) as exc:
        predictor.ensure_models_available()

    assert "Run `python fix_ml_models.py`" in str(exc.value)


def test_compute_hash_matches_stub_provenance(tmp_path: Path) -> None:
    model_dir = tmp_path / "trained_models"
    details = _write_stub_artifacts(model_dir)

    provenance = load_provenance(model_dir)
    assert provenance["artifact_hash"] == details["artifact_hash"]

    actual_hash = compute_artifact_hash(model_dir)
    assert actual_hash == details["artifact_hash"]


def test_predictor_uses_stub_artifacts(tmp_path: Path) -> None:
    model_dir = tmp_path / "trained_models"
    details = _write_stub_artifacts(model_dir)

    predictor = CrateQualityPredictor(model_dir=str(model_dir))
    predictor.ensure_models_available()

    sample = {"name": "test-crate", "description": "A demo crate"}
    prediction = predictor.predict_quality(sample)

    assert prediction.model_version == details["version"]
    assert prediction.security_risk in {"low", "medium", "high"}
    assert prediction.confidence == 1.0
    assert prediction.features_used


def test_artifact_manifest_lists_expected_files(tmp_path: Path) -> None:
    model_dir = tmp_path / "trained_models"
    _write_stub_artifacts(model_dir)

    for name in ARTIFACT_FILENAMES:
        assert (model_dir / name).exists(), f"Expected artifact missing: {name}"


def test_predictor_detects_stale_artifacts(tmp_path: Path) -> None:
    model_dir = tmp_path / "trained_models"
    _write_stub_artifacts(model_dir)

    # Tamper with an artifact without updating provenance hash
    tampered_path = model_dir / "quality_model.pkl"
    with tampered_path.open("wb") as handle:
        pickle.dump(_StubRegressor(0.1), handle)

    predictor = CrateQualityPredictor(model_dir=str(model_dir))

    with pytest.raises(RuntimeError) as exc:
        predictor.ensure_models_available()

    assert "stale or corrupted" in str(exc.value)
