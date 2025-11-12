import asyncio
import logging
import time
from typing import Optional
from urllib.parse import urlparse

import aiohttp
import requests

from ..config import DEFAULT_HTTP_TIMEOUT
from ..exceptions import ValidationError as PipelineValidationError

_session: Optional[requests.Session] = None


def get_session() -> requests.Session:
    """Return a singleton requests.Session"""
    global _session
    if _session is None:
        _session = requests.Session()
    return _session


def get_with_retry(
    url: str,
    retries: int = 3,
    backoff_factor: float = 0.5,
    status_forcelist: tuple[int, ...] = (500, 502, 503, 504),
    **kwargs,
) -> requests.Response:
    """GET a URL with retry and exponential backoff."""
    # Validate URL
    try:
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            raise PipelineValidationError(f"Invalid URL: {url}")
        if parsed.scheme not in ("http", "https"):
            raise PipelineValidationError(
                f"URL scheme '{parsed.scheme}' not allowed. Only http and https are supported."
            )
    except Exception as e:
        if isinstance(e, PipelineValidationError):
            raise
        raise PipelineValidationError(f"Invalid URL format: {e}") from e

    session = get_session()
    # Ensure timeout is set, allow override via kwargs
    kwargs.setdefault("timeout", DEFAULT_HTTP_TIMEOUT)
    for attempt in range(retries):
        try:
            response = session.get(url, **kwargs)
            if response.status_code in status_forcelist:
                raise requests.HTTPError(f"{response.status_code} error", response=response)
            return response
        except requests.RequestException as e:
            if attempt == retries - 1:
                raise
            sleep_time = backoff_factor * (2 ** attempt)
            logging.warning(
                "GET %s failed on attempt %d/%d: %s", url, attempt + 1, retries, e
            )
            time.sleep(sleep_time)
    # Should never reach here
    raise RuntimeError("Unhandled retry logic in get_with_retry")


async def async_get_with_retry(
    url: str,
    *,
    session: aiohttp.ClientSession,
    retries: int = 3,
    backoff_factor: float = 0.5,
    status_forcelist: tuple[int, ...] = (500, 502, 503, 504),
    **kwargs,
) -> aiohttp.ClientResponse:
    """Asynchronous variant of :func:`get_with_retry` using ``aiohttp``."""

    last_error: Optional[Exception] = None
    for attempt in range(retries):
        try:
            response = await session.get(url, **kwargs)
            if response.status in status_forcelist:
                error_text = await response.text()
                await response.release()
                raise aiohttp.ClientResponseError(
                    request_info=response.request_info,
                    history=response.history,
                    status=response.status,
                    message=error_text,
                    headers=response.headers,
                )
            return response
        except aiohttp.ClientError as exc:
            last_error = exc
            logging.warning(
                "Async GET %s failed on attempt %d/%d: %s",
                url,
                attempt + 1,
                retries,
                exc,
            )
            if attempt == retries - 1:
                break
            sleep_time = backoff_factor * (2 ** attempt)
            await asyncio.sleep(sleep_time)

    if last_error:
        raise last_error
    raise RuntimeError("Unhandled retry logic in async_get_with_retry")
