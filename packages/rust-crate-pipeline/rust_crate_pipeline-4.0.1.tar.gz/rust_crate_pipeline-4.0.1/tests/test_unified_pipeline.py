import asyncio
import time
import ssl
from typing import Any, Dict, Optional
from unittest.mock import AsyncMock, Mock, patch

import pytest

import aiohttp
from aiohttp.client_reqrep import ConnectionKey

from rust_crate_pipeline.config import CrateMetadata
from rust_crate_pipeline.core.sacred_chain import (SacredChainTrace,
                                                   TrustVerdict)
from rust_crate_pipeline.unified_pipeline import (LLMConfig, PipelineConfig,
                                                  UnifiedSigilPipeline)


@pytest.fixture
def sample_crate_metadata():
    """Provides a sample CrateMetadata object for testing."""
    return CrateMetadata(
        name="test-crate",
        version="1.0.0",
        description="A test crate for testing.",
        repository="https://github.com/test/test-crate",
        keywords=["test", "testing"],
        categories=["testing"],
        readme="This is a test README.",
        downloads=100,
        github_stars=10,
        dependencies=[],
        features={},
        code_snippets=[],
        readme_sections={},
        librs_downloads=None,
        source="crates.io",
    )


@pytest.fixture
def mock_pipeline_config():
    """Provides a mock PipelineConfig object for testing."""
    config = Mock(spec=PipelineConfig)
    config.skip_source_analysis = False
    return config


@pytest.fixture
def mock_llm_config():
    """Provides a mock LLMConfig object for testing."""
    return Mock(spec=LLMConfig)


@pytest.fixture
def sanitized_documentation_with_metadata():
    """Sanitized scraper output that includes structured metadata."""

    docs_rs_readme = "Comprehensive docs content for testing. " * 10

    return {
        "crates_io": {
            "url": "https://crates.io/crates/demo-crate",
            "content": "Rendered crates.io README content.",
            "error": None,
            "status_code": 200,
            "structured_data": {
                "crate": {
                    "description": "Structured description from crates.io.",
                    "keywords": ["cli", "parser"],
                    "categories": ["command-line-utilities"],
                    "downloads": 424242,
                    "dependencies": [{"name": "serde", "version": "1.0"}],
                    "features": {"default": ["std"]},
                    "repository": "https://github.com/demo/demo-crate",
                }
            },
        },
        "lib_rs": {
            "url": "https://lib.rs/crates/demo-crate",
            "content": "Lib.rs overview." * 5,
            "error": None,
            "status_code": 200,
            "structured_data": {"stats": {"downloads": 99999}},
        },
        "docs_rs": {
            "url": "https://docs.rs/demo-crate",
            "content": docs_rs_readme,
            "error": None,
            "status_code": 200,
        },
    }


@pytest.mark.asyncio
@patch("rust_crate_pipeline.unified_pipeline.IRLEngine")
@patch("rust_crate_pipeline.unified_pipeline.UnifiedScraper")
@patch("rust_crate_pipeline.unified_pipeline.UnifiedLLMProcessor")
async def test_unified_sigil_pipeline_initialization(
    mock_llm_processor,
    mock_scraper,
    mock_irl_engine,
    mock_pipeline_config,
    mock_llm_config,
):
    """Tests that the UnifiedSigilPipeline class initializes correctly."""
    pipeline = UnifiedSigilPipeline(mock_pipeline_config, mock_llm_config)
    assert pipeline.config == mock_pipeline_config
    assert pipeline.llm_config == mock_llm_config
    assert pipeline.irl_engine is not None
    assert pipeline.scraper is not None
    assert pipeline.unified_llm_processor is not None


@pytest.mark.asyncio
@patch("rust_crate_pipeline.unified_pipeline.IRLEngine")
@patch("rust_crate_pipeline.unified_pipeline.UnifiedScraper")
@patch("rust_crate_pipeline.unified_pipeline.UnifiedLLMProcessor")
async def test_analyze_crate(
    mock_llm_processor,
    mock_scraper,
    mock_irl_engine,
    mock_pipeline_config,
    mock_llm_config,
):
    """Tests the analyze_crate method."""
    mock_scraper_instance = mock_scraper.return_value
    mock_scraper_instance.scrape_crate_documentation = AsyncMock(return_value={})
    mock_scraper_instance.__aenter__ = AsyncMock(return_value=mock_scraper_instance)
    mock_scraper_instance.__aexit__ = AsyncMock(return_value=None)

    mock_irl_engine_instance = mock_irl_engine.return_value
    mock_irl_engine_instance.analyze_with_sacred_chain = AsyncMock(
        return_value=SacredChainTrace(
            input_data="test-crate",
            context_sources=[],
            reasoning_steps=[],
            suggestion="",
            verdict=TrustVerdict.DEFER,
            audit_info={},
            irl_score=0.0,
            execution_id="",
            timestamp="",
            canon_version="",
        )
    )
    mock_irl_engine_instance.__aenter__ = AsyncMock(
        return_value=mock_irl_engine_instance
    )
    mock_irl_engine_instance.__aexit__ = AsyncMock(return_value=None)

    pipeline = UnifiedSigilPipeline(mock_pipeline_config, mock_llm_config)
    async with pipeline:
        pipeline._get_latest_crate_version = AsyncMock(return_value="1.0.0")
        pipeline._add_crate_analysis_results = AsyncMock()
        trace = await pipeline.analyze_crate("test-crate")

    assert isinstance(trace, SacredChainTrace)
    assert trace.input_data == "test-crate"


@pytest.mark.asyncio
async def test_download_crate_rejects_intercepted_certificate(tmp_path):
    """Ensure TLS interception attempts are rejected during crate downloads."""

    pipeline = object.__new__(UnifiedSigilPipeline)
    pipeline.logger = Mock()

    certificate_error = aiohttp.ClientConnectorCertificateError(
        connection_key=ConnectionKey(
            host="static.crates.io",
            port=443,
            is_ssl=True,
            ssl=None,
            proxy=None,
            proxy_auth=None,
            proxy_headers_hash=None,
        ),
        certificate_error=ssl.SSLError("certificate verify failed"),
    )

    class FakeResponse:
        async def __aenter__(self):
            raise certificate_error

        async def __aexit__(self, exc_type, exc, tb):
            return False

    class FakeSession:
        def __init__(self, *args, **kwargs):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        def get(self, url):
            return FakeResponse()

    with patch("aiohttp.ClientSession", FakeSession):
        crate_path = await UnifiedSigilPipeline._download_and_extract_crate(
            pipeline,
            crate_name="serde",
            crate_version="1.0.0",
            target_dir=tmp_path,
        )

    assert crate_path is None
    pipeline.logger.warning.assert_called()
    warning_message = "".join(
        call_arg[0][0] for call_arg in pipeline.logger.warning.call_args_list
    )
    assert "certificate verify failed" in warning_message


@pytest.mark.asyncio
async def test_concurrent_crate_analysis_latency(
    mock_pipeline_config, mock_llm_config, tmp_path
):
    """Ensure multiple crate analyses run concurrently without starving the loop."""

    class SlowCrateAnalyzer:
        def __init__(self, crate_source_path: str):
            self.crate_source_path = crate_source_path
            self.logger = Mock()

        def analyze(self) -> Dict[str, Any]:
            time.sleep(0.05)
            return {"status": "completed", "crate_path": self.crate_source_path}

        async def analyze_async(self) -> Dict[str, Any]:
            return await asyncio.to_thread(self.analyze)

    pipeline = UnifiedSigilPipeline(mock_pipeline_config, mock_llm_config)

    crate_dirs = []
    for idx in range(3):
        crate_dir = tmp_path / f"crate-{idx}"
        crate_dir.mkdir()
        crate_dirs.append(crate_dir)

    async with pipeline:
        pipeline._download_and_extract_crate = AsyncMock(side_effect=crate_dirs)
        pipeline._handle_toolchain_override = AsyncMock(return_value=None)
        pipeline._restore_toolchain_override = AsyncMock()
        pipeline._run_command = AsyncMock(return_value=({}, None))
        pipeline.sanitizer.sanitize_data = Mock(side_effect=lambda data: data)

        latencies: list[float] = []

        async def monitor_latency() -> None:
            loop = asyncio.get_running_loop()
            for _ in range(10):
                start = loop.time()
                await asyncio.sleep(0.01)
                latencies.append(loop.time() - start)

        async def run_analysis(idx: int) -> SacredChainTrace:
            trace = SacredChainTrace(
                input_data=f"crate-{idx}",
                context_sources=[],
                reasoning_steps=[],
                suggestion="",
                verdict=TrustVerdict.DEFER,
                audit_info={"should_analyze_source_code": True},
                irl_score=0.0,
                execution_id=f"exec-{idx}",
                timestamp="",
                canon_version="",
            )
            await pipeline._add_crate_analysis_results(
                trace.input_data, "1.0.0", trace
            )
            return trace

        patch_targets = [
            patch("rust_crate_pipeline.unified_pipeline.CrateAnalyzer", SlowCrateAnalyzer),
            patch("rust_crate_pipeline.crate_analysis.CrateAnalyzer", SlowCrateAnalyzer),
        ]
        with patch_targets[0], patch_targets[1]:
            monitor_task = asyncio.create_task(monitor_latency())
            traces = await asyncio.gather(*(run_analysis(i) for i in range(3)))
            await monitor_task

        assert latencies and max(latencies) < 0.06
        for idx, trace in enumerate(traces):
            crate_analysis = trace.audit_info.get("crate_analysis", {})
            assert crate_analysis.get("status") == "completed"
            assert crate_analysis.get("enhanced_analysis", {}).get(
                "crate_path"
            ) == str(crate_dirs[idx])


@pytest.mark.asyncio
async def test_concurrent_crate_downloads_streaming(tmp_path):
    """Ensure concurrent crate downloads remain responsive under load."""

    pipeline = object.__new__(UnifiedSigilPipeline)
    pipeline.logger = Mock()

    payload = b"x" * (65536 * 3 + 123)

    class FakeStream:
        def __init__(self, data: bytes, delay: float) -> None:
            self._data = data
            self._delay = delay

        async def iter_chunked(self, chunk_size: int):
            for start in range(0, len(self._data), chunk_size):
                await asyncio.sleep(self._delay)
                yield self._data[start : start + chunk_size]

    class FakeResponse:
        status = 200

        def __init__(self, data: bytes, delay: float) -> None:
            self.content = FakeStream(data, delay)

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

    class FakeSession:
        def __init__(self, *args, **kwargs):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        def get(self, url):
            return FakeResponse(payload, 0.05)

    async def monitor_latency(tasks):
        while any(not task.done() for task in tasks):
            start = time.perf_counter()
            await asyncio.sleep(0.05)
            elapsed = time.perf_counter() - start
            assert elapsed < 0.2, f"Event loop blocked for {elapsed:.3f}s"

    def slow_extract(self, crate_file_path, target_dir, crate_name, crate_version):
        time.sleep(0.2)
        crate_dir = target_dir / f"{crate_name}-{crate_version}"
        crate_dir.mkdir(exist_ok=True)
        return crate_dir

    with patch("aiohttp.ClientSession", FakeSession), patch.object(
        UnifiedSigilPipeline, "_extract_crate_tarball", slow_extract
    ):
        download_tasks = []
        for idx in range(3):
            target_dir = tmp_path / f"target_{idx}"
            target_dir.mkdir()
            download_tasks.append(
                asyncio.create_task(
                    pipeline._download_and_extract_crate(
                        "stream-crate", "1.0.0", target_dir
                    )
                )
            )

        monitor_task = asyncio.create_task(monitor_latency(download_tasks))
        results = await asyncio.gather(*download_tasks)
        await monitor_task

    for path in results:
        assert path is not None
        assert path.is_dir()


@patch("rust_crate_pipeline.unified_pipeline.IRLEngine")
@patch("rust_crate_pipeline.unified_pipeline.UnifiedScraper")
@patch("rust_crate_pipeline.unified_pipeline.UnifiedLLMProcessor")
def test_extract_readme_content_with_sanitized_dict(
    mock_llm_processor,
    mock_scraper,
    mock_irl_engine,
    mock_pipeline_config,
    mock_llm_config,
):
    """Ensure sanitized documentation dicts are handled correctly."""

    pipeline = UnifiedSigilPipeline(mock_pipeline_config, mock_llm_config)

    sanitized_documentation = {
        "docs_rs": {
            "content": "This is a sanitized README "
            + "content " * 10
            + "with sufficient length to pass validation.",
            "error": None,
        },
        "lib_rs": {"content": "Short", "error": None},
        "crates_io": {"content": None, "error": "Not available"},
    }

    readme = pipeline._extract_readme_content(sanitized_documentation)

    assert "sanitized README" in readme


@pytest.mark.asyncio
@patch("rust_crate_pipeline.unified_pipeline.IRLEngine")
@patch("rust_crate_pipeline.unified_pipeline.UnifiedScraper")
@patch("rust_crate_pipeline.unified_pipeline.UnifiedLLMProcessor")
async def test_add_unified_llm_enrichment_uses_sanitized_metadata(
    mock_llm_processor,
    mock_scraper,
    mock_irl_engine,
    mock_pipeline_config,
    mock_llm_config,
    sanitized_documentation_with_metadata,
):
    """Ensure metadata is populated from sanitized scraper output."""

    class DummyProcessor:
        def __init__(self) -> None:
            self.last_crate_metadata: Optional[CrateMetadata] = None

        async def process_crate(self, crate_metadata: CrateMetadata) -> Any:
            self.last_crate_metadata = crate_metadata

            class Result:
                def to_dict(self) -> Dict[str, Any]:
                    return {"status": "ok"}

            return Result()

    dummy_processor = DummyProcessor()
    mock_llm_processor.return_value = dummy_processor

    pipeline = UnifiedSigilPipeline(mock_pipeline_config, mock_llm_config)

    trace = SacredChainTrace(
        input_data="demo-crate",
        context_sources=[],
        reasoning_steps=[],
        suggestion="Fallback description",
        verdict=TrustVerdict.DEFER,
        audit_info={"sanitized_documentation": sanitized_documentation_with_metadata},
        irl_score=0.0,
        execution_id="exec-test",
        timestamp="2024-01-01T00:00:00Z",
        canon_version="1.0.0",
    )

    await pipeline._add_unified_llm_enrichment("demo-crate", "2.0.0", trace)

    crate_metadata = trace.audit_info["crate_metadata"]

    assert crate_metadata["description"] == "Structured description from crates.io."
    assert crate_metadata["repository"] == "https://github.com/demo/demo-crate"
    assert crate_metadata["keywords"] == ["cli", "parser"]
    assert crate_metadata["categories"] == ["command-line-utilities"]
    assert crate_metadata["downloads"] == 424242
    assert crate_metadata["librs_downloads"] == 99999
    assert "Comprehensive docs content" in crate_metadata["readme"]

    assert dummy_processor.last_crate_metadata is not None
    assert (
        dummy_processor.last_crate_metadata.description
        == "Structured description from crates.io."
    )
    assert dummy_processor.last_crate_metadata.downloads == 424242
