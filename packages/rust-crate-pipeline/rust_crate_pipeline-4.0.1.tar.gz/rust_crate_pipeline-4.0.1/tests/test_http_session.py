from unittest.mock import AsyncMock, Mock

import aiohttp
import pytest
import requests

from rust_crate_pipeline.exceptions import ValidationError as PipelineValidationError
from rust_crate_pipeline.utils import http_session


def test_get_with_retry_eventual_success(monkeypatch):
    session = requests.Session()
    calls = {"count": 0}

    def fake_get(url, **kwargs):
        calls["count"] += 1
        if calls["count"] < 3:
            raise requests.RequestException("boom")
        return Mock(status_code=200)

    monkeypatch.setattr(session, "get", fake_get)
    monkeypatch.setattr(http_session, "_session", session)
    monkeypatch.setattr(http_session.time, "sleep", lambda _: None)

    resp = http_session.get_with_retry("http://example.com")
    assert resp.status_code == 200
    assert calls["count"] == 3


def test_get_with_retry_invalid_url():
    """Test that invalid URLs raise ValidationError."""
    with pytest.raises(PipelineValidationError):
        http_session.get_with_retry("not-a-url")
    with pytest.raises(PipelineValidationError):
        http_session.get_with_retry("ftp://example.com")
    with pytest.raises(PipelineValidationError):
        http_session.get_with_retry("http://")


@pytest.mark.asyncio
async def test_async_get_with_retry_success():
    session = AsyncMock()
    response = AsyncMock()
    response.status = 200
    session.get.return_value = response

    result = await http_session.async_get_with_retry(
        "http://example.com", session=session
    )

    assert result is response
    session.get.assert_called_once_with("http://example.com")


@pytest.mark.asyncio
async def test_async_get_with_retry_forcelist():
    session = AsyncMock()
    response = AsyncMock()
    response.status = 500
    response.text = AsyncMock(return_value="boom")
    response.release = AsyncMock()
    response.history = tuple()
    response.headers = {}
    response.request_info = Mock(real_url="http://example.com")
    session.get.return_value = response

    with pytest.raises(aiohttp.ClientResponseError):
        await http_session.async_get_with_retry(
            "http://example.com", session=session, retries=1
        )

    response.text.assert_awaited()
    response.release.assert_awaited()


def test_get_with_retry_all_fail(monkeypatch):
    session = requests.Session()
    calls = {"count": 0}

    def fake_get(url, **kwargs):
        calls["count"] += 1
        raise requests.RequestException("boom")

    monkeypatch.setattr(session, "get", fake_get)
    monkeypatch.setattr(http_session, "_session", session)
    monkeypatch.setattr(http_session.time, "sleep", lambda _: None)

    try:
        http_session.get_with_retry("http://example.com")
    except requests.RequestException:
        pass
    else:
        assert False, "Expected RequestException"

    assert calls["count"] == 3
