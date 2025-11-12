"""Tests for Rule Zero override enforcement."""

import pytest

from rust_crate_pipeline import main as pipeline_main


def test_enforce_rule_zero_exits_without_authorised_override(monkeypatch, tmp_path):
    """A hash mismatch without a valid override must terminate the pipeline."""

    monkeypatch.setattr(pipeline_main, "PROJECT_ROOT", tmp_path)

    db_path = tmp_path / "sigil_rag_cache.db"
    db_path.write_bytes(b"not-real")

    hash_path = tmp_path / "sigil_rag_cache.hash"
    hash_path.write_text("different-hash", encoding="utf-8")

    monkeypatch.setenv("ENFORCE_RULE_ZERO", "true")

    for var in [
        "RULE_ZERO_OVERRIDE",
        "RULE_ZERO_OVERRIDE_JUSTIFICATION",
        "RULE_ZERO_OVERRIDE_OPERATOR",
        "RULE_ZERO_OVERRIDE_TOKEN",
        "RULE_ZERO_OVERRIDE_SECRET",
        "RULE_ZERO_OVERRIDE_ALLOWLIST",
        "RULE_ZERO_OVERRIDE_ALLOWLIST_PATH",
    ]:
        monkeypatch.delenv(var, raising=False)

    with pytest.raises(SystemExit) as excinfo:
        pipeline_main.enforce_rule_zero_reinforcement()

    assert excinfo.value.code == 1
    assert not (tmp_path / "rule_zero_override_audit.log").exists()
