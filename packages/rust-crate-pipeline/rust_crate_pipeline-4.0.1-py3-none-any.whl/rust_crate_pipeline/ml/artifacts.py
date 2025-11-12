"""Helpers for managing ML model artifacts."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Dict, Iterable, Sequence

ARTIFACT_FILENAMES: Sequence[str] = (
    "quality_model.pkl",
    "security_model.pkl",
    "maintenance_model.pkl",
    "popularity_model.pkl",
    "dependency_model.pkl",
    "text_vectorizer.pkl",
    "feature_scaler.pkl",
)

PROVENANCE_FILENAME = "model_provenance.json"
LEGACY_METADATA_FILENAME = "model_metadata.json"


def compute_artifact_hash(model_dir: Path, filenames: Iterable[str] | None = None) -> str:
    """Compute a deterministic hash for the trained model artifacts."""

    filenames = tuple(sorted(filenames or ARTIFACT_FILENAMES))
    hasher = hashlib.sha256()
    for name in filenames:
        path = model_dir / name
        if not path.exists():
            raise FileNotFoundError(f"Missing artifact file: {path}")
        hasher.update(name.encode("utf-8"))
        hasher.update(path.read_bytes())
    return hasher.hexdigest()


def load_provenance(model_dir: Path) -> Dict[str, object]:
    """Load provenance metadata for trained models."""

    provenance_path = model_dir / PROVENANCE_FILENAME
    if not provenance_path.exists():
        raise FileNotFoundError(
            f"Model provenance file not found: {provenance_path}. Run fix_ml_models.py first."
        )
    with provenance_path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def ensure_required_artifacts_exist(model_dir: Path) -> None:
    """Verify that all required artifact files exist."""

    missing = [name for name in ARTIFACT_FILENAMES if not (model_dir / name).exists()]
    if missing:
        missing_paths = ", ".join(str(model_dir / name) for name in missing)
        raise FileNotFoundError(
            "Missing trained model artifacts: "
            f"{missing_paths}. Run fix_ml_models.py to generate them."
        )
