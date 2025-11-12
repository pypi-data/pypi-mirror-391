import logging
import ssl
from pathlib import Path
from typing import AsyncIterator
from unittest.mock import Mock, patch

import pytest
import pytest_asyncio
from aiohttp import web

from rust_crate_pipeline.config import PipelineConfig
from rust_crate_pipeline.unified_pipeline import UnifiedSigilPipeline


SELF_SIGNED_CERT = """-----BEGIN CERTIFICATE-----
MIIDCTCCAfGgAwIBAgIUSpyHhH78M7kiHQW7U7F8Gzkmx3owDQYJKoZIhvcNAQEL
BQAwFDESMBAGA1UEAwwJbG9jYWxob3N0MB4XDTI1MTAzMDIxMDcyNloXDTI1MTAz
MTIxMDcyNlowFDESMBAGA1UEAwwJbG9jYWxob3N0MIIBIjANBgkqhkiG9w0BAQEF
AAOCAQ8AMIIBCgKCAQEAxjP0ehJ96d3TQqHsyi9y21dyBENwRqK7wLKSrHuWb9Yp
5SU8hsK60geT0NwdjPdZlzWZMrKwsUwxfFahlhJEpbS+DeDk4kfUj55Zr1ODGjjD
UwkqCvOoerZo2qIOQm+1BK0vv8atmjFIrsXx+xdLttY5eWEcuPm/QngCBplGzkZj
7Hrb11VE+y+acMM9C5fYnN+uXMJKIl0k/Z+94Vo6B6ISPvTIDgZvrOWcgyGDVdKo
cUb3LHZTHi48JTZjCIzXhGU0GI1zYScVDjMVgwSca4GGnEtbHxzg4PNAeqJ6rtK/
gTy1HDEM8o4nSaqgmEb/o8wghwy8fUWrEYDLQzy3PQIDAQABo1MwUTAdBgNVHQ4E
FgQUJ6UGd4mZd0/zH77utvUcpu5prG0wHwYDVR0jBBgwFoAUJ6UGd4mZd0/zH77u
tvUcpu5prG0wDwYDVR0TAQH/BAUwAwEB/zANBgkqhkiG9w0BAQsFAAOCAQEAST5a
YdnH6n+jA8BNrh3duU+VMTNJ3IC4M/KyzsWyxgK0IdX2ha7ZJYWqyUvxdz0c/F5o
InNKA5GfutWbhHXs19Yk8O00XSNq6NoEg4TQpLazhZ2ngbqoERdzvgL3Ct5OqelE
Oov/QAXfcQDtEhf7FlvyZJxdWZ83wTDKOqi9fIML8dfa4M/hSzQllhJbG1UoaJyD
iqFHtvnJAgEwA1vlymK4eB72qVi8xbsNF+f0ftJ2FxKNa4lk7Y+UEad/bs8RsRg6
OxnhUBJztb6GB7RzMrX0eFqfsbalaeUPbHA651WzaaEWAs7gl/wMfqY9SuQRuV82
5BFFDRq4qb+Pmn/5Tg==
-----END CERTIFICATE-----
"""


SELF_SIGNED_KEY = """-----BEGIN PRIVATE KEY-----
MIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQDGM/R6En3p3dNC
oezKL3LbV3IEQ3BGorvAspKse5Zv1inlJTyGwrrSB5PQ3B2M91mXNZkysrCxTDF8
VqGWEkSltL4N4OTiR9SPnlmvU4MaOMNTCSoK86h6tmjaog5Cb7UErS+/xq2aMUiu
xfH7F0u21jl5YRy4+b9CeAIGmUbORmPsetvXVUT7L5pwwz0Ll9ic365cwkoiXST9
n73hWjoHohI+9MgOBm+s5ZyDIYNV0qhxRvcsdlMeLjwlNmMIjNeEZTQYjXNhJxUO
MxWDBJxrgYacS1sfHODg80B6onqu0r+BPLUcMQzyjidJqqCYRv+jzCCHDLx9RasR
gMtDPLc9AgMBAAECggEAALFcTKlFYudOrn2HPh1Z2FiZ0lgpAOTfOqPKfaCwodic
t2DAsX47QxzZ1axQocuYjCiDY1O6veKUtrOifMuODV/lx9cjfa3/bnbA0gB8+r8R
jGKsZgg8LHJNngax0uYgkBu0iRtTmTB3FFNRTqMiIDQR/zG0H7+8Z9SoZH0DLBk9
0CzM278OE43fTfEKMC4oX0CQryIYeoLOCAt3yUXed4VaGF2NnIMVkzbx64nFq7AD
FhTL98ouUDAQqbQVagfzDGVJxY8+FjRjnWX3VREc4+xJxs6LddlElzpRrvrzIrrf
qW+OdULzZZOCP9I4p+iB99axx1ZjKQy0K/a0bSkKAQKBgQDu2BuO/yyazVM77wpx
kxcU3p6XkFfRhrmPL66KYCrX/NEmD2gB7u4CdSaU5kjqehCss27fgGbEiYt0OZI0
TR0ZmOKNmdOlaytakWg6fLlnJKvUBodD0qzNGYfOR4T1e1cEhuqqOCyWxvTApsvY
WmL9MK8+W/D7Ra2OegBOKh+qAQKBgQDUcIg83jc0QRoVJWxJmFZtbI+SPxzF9/tC
570NzKEBsCD5KqJ/dcMewIYqjaNgMMNCsQfPfzHODV5Qm18jhatwbVKY4fsbl8Sd
NFgN7U304y2SEkmFBoZ+sOQkSs5rw3Gbh0Du4JSgypNbR1yGuTD5xkcfyAY+0d4U
lQhLVX81PQKBgQDBMbcg9NEMqnbgLNwCwFrUO7qGmHAggFyKMKR7M4yURuCaa63S
moSVIlPB74Adgf0I5N8TFFaMNUHDEmprudCHCv5+UWY8ELLxwFpRrN9/Sc9fYqR5
POkfwb3zIjCvLERX2hXo+CVBFM+XIZQTfhFCAeZOh6omZdccPx0OHM6eAQKBgQDP
jFHOBdwxNRliZ3lwPWDS7yklXHuj/i6Aox9VCAKVP5o3VKwFkuvac4WgtVhUdc+O
rJ5Q3peuE+l9Hw7ICaQA5w23R7CouJHidG1CzgFHq1uuRieFy2ZDCFccDem15vBr
XqzVtJwAq2lj2EhRZ0SuAkUii61uWmN6AFBmKVVqkQKBgF5tb1RRWoupvypnZGQq
YeQDB3wl6/Nx89LF5bmnTIpiN1/TPRWZCORM62fjMlA7BAvwGA61dcKzmGxUa/0R
NMquQASrtYAWmBwC+ci0+OuI8Ol9CzJBiXOR3UCehvT0uFnqIEUknLFrVVA7QoO8
5A9MvHX6F+zPtdir/oeOe3Ij
-----END PRIVATE KEY-----
"""


@pytest.fixture
def pipeline_stub() -> UnifiedSigilPipeline:
    with patch.object(UnifiedSigilPipeline, "_initialize_components", lambda self: None):
        pipeline = UnifiedSigilPipeline(PipelineConfig(), None)

    logger = Mock(spec=logging.Logger)
    logger.warning = Mock()
    logger.error = Mock()
    logger.info = Mock()
    pipeline.logger = logger
    return pipeline


@pytest_asyncio.fixture
async def self_signed_crate_host(tmp_path: Path) -> AsyncIterator[str]:
    cert_path = tmp_path / "cert.pem"
    key_path = tmp_path / "key.pem"
    cert_path.write_text(SELF_SIGNED_CERT)
    key_path.write_text(SELF_SIGNED_KEY)

    app = web.Application()

    async def handle(request: web.Request) -> web.Response:
        return web.Response(body=b"dummy crate content", content_type="application/octet-stream")

    app.router.add_get("/crates/{crate}/{filename}", handle)

    runner = web.AppRunner(app)
    await runner.setup()

    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ssl_context.load_cert_chain(certfile=str(cert_path), keyfile=str(key_path))

    site = web.TCPSite(runner, host="127.0.0.1", port=0, ssl_context=ssl_context)
    await site.start()

    if not site._server or not site._server.sockets:
        raise RuntimeError("Failed to bind HTTPS test server")

    port = site._server.sockets[0].getsockname()[1]
    try:
        yield f"https://localhost:{port}/crates"
    finally:
        await runner.cleanup()


@pytest.mark.asyncio
async def test_self_signed_certificate_rejected(
    pipeline_stub: UnifiedSigilPipeline, self_signed_crate_host: str, tmp_path: Path
) -> None:
    crate_dir = await pipeline_stub._download_and_extract_crate(
        crate_name="dummy-crate",
        crate_version="0.1.0",
        target_dir=tmp_path,
        crate_registry_base=self_signed_crate_host,
    )

    assert crate_dir is None
    assert pipeline_stub.logger.warning.called
    logged_messages = " ".join(str(call.args[0]) for call in pipeline_stub.logger.warning.call_args_list)
    assert "certificate" in logged_messages.lower()


@pytest.mark.asyncio
@pytest.mark.live
async def test_crates_io_download_succeeds(
    pipeline_stub: UnifiedSigilPipeline, tmp_path: Path
) -> None:
    crate_dir = await pipeline_stub._download_and_extract_crate(
        crate_name="cfg-if",
        crate_version="1.0.0",
        target_dir=tmp_path,
    )

    assert crate_dir is not None
    assert crate_dir.exists()
