from __future__ import annotations

import hashlib
import json
from typing import Any, Dict

import pytest

from tools.codex_guard import codex_envelope
from tools.codex_task_runner import (
    EnvelopeValidationError,
    run_codex_task,
    validate_envelope,
)


def build_valid_envelope(**overrides: Any) -> Dict[str, Any]:
    base = codex_envelope(
        input_text="prompt",
        context={"task": "demo"},
        reasoning="reason",
        suggestion={"action": "test"},
        verdict="Allow",
        loa_signature="sig",
        trust_score=0.7,
        allowed=True,
    )
    base.update(overrides)
    return base


def test_codex_envelope_structure_validates() -> None:
    envelope = build_valid_envelope()
    validated = validate_envelope(envelope)
    assert validated == envelope


@pytest.mark.parametrize(
    "modifier",
    [
        lambda env: env.pop("audit"),
        lambda env: env["audit"].pop("hash"),
        lambda env: env.update({"verdict": "INVALID"}),
        lambda env: env.update({"IRL": {"model_id": "sigil_trust_v1", "score": "bad", "allowed": True}}),
    ],
)
def test_validate_envelope_rejects_malformed(modifier) -> None:
    envelope = build_valid_envelope()
    modifier(envelope)
    with pytest.raises(EnvelopeValidationError):
        validate_envelope(envelope)


def test_run_codex_task_returns_valid_envelope(caplog) -> None:
    def successful_task(**kwargs: Any) -> Dict[str, Any]:
        return codex_envelope(
            input_text=kwargs["input_text"],
            context=kwargs["context"],
            reasoning="Handled successfully",
            suggestion={"status": "ok"},
            verdict="Allow",
            loa_signature="sig",
            trust_score=1.0,
            allowed=True,
        )

    result = run_codex_task(successful_task, input_text="hello", context={"example": True})
    assert result["verdict"] == "Allow"
    validate_envelope(result)
    assert "Invalid Codex envelope" not in "".join(caplog.messages)


def test_run_codex_task_falls_back_on_invalid(caplog) -> None:
    def broken_task(**kwargs: Any) -> Dict[str, Any]:
        return {"not": "an envelope"}

    result = run_codex_task(
        broken_task,
        input_text="hello",
        context={"example": True},
        loa_signature="sig",
        trust_score=0.2,
        allowed=False,
    )
    assert result["verdict"] == "Manual Review"
    assert result["suggestion"] == {}
    assert any("Invalid Codex envelope" in message for message in caplog.messages)
    validate_envelope(result)
    expected_hash = result["audit"]["hash"]
    assert expected_hash == hashlib.sha256(
        json.dumps({}, sort_keys=True).encode("utf-8")
    ).hexdigest()
