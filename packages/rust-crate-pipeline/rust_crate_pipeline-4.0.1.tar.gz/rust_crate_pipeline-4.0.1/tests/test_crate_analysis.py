import asyncio
import time
from pathlib import Path
from types import MethodType
from unittest.mock import AsyncMock, Mock, patch

import pytest

from rust_crate_pipeline.crate_analysis import CrateAnalyzer
# Import test utilities for subprocess cleanup
from tests.test_utils import get_test_logger, run_command_for_tests


@pytest.fixture
def crate_analyzer(tmpdir):
    """Provides a CrateAnalyzer instance for the tests."""
    # Create a minimal Cargo.toml so analysis does not exit early
    tmpdir.join("Cargo.toml").write("""[package]\nname = 'test-crate'\nversion = '0.1.0'\n""")
    return CrateAnalyzer(str(tmpdir))


class TestCrateAnalyzer:
    """Test CrateAnalyzer class."""

    def test_initialization(self, crate_analyzer):
        """Test CrateAnalyzer initialization."""
        assert crate_analyzer.crate_source_path is not None

    @patch("subprocess.run")
    def test_run_cargo_cmd(self, mock_run, crate_analyzer):
        """Test run_cargo_cmd method."""
        mock_run.return_value = Mock(
            stdout='{"reason": "compiler-message"}', stderr="", returncode=0
        )
        result = crate_analyzer.run_cargo_cmd(["test", "command"])
        assert "cmd" in result
        assert "returncode" in result
        assert "stdout" in result
        assert "stderr" in result

    @patch("rust_crate_pipeline.crate_analysis.CrateAnalyzer.run_cargo_cmd")
    def test_analyze(self, mock_run_cargo_cmd, crate_analyzer):
        """Test analyze method."""
        mock_run_cargo_cmd.return_value = {}
        results = crate_analyzer.analyze()
        assert "build" in results
        assert "test" in results
        assert "clippy" in results
        assert "fmt" in results
        assert "audit" in results
        assert "tree" in results
        assert "doc" in results

    @pytest.mark.asyncio
    async def test_run_cargo_cmd_async_offloads_blocking_work(self, crate_analyzer):
        """Ensure the async wrapper prevents event loop starvation."""

        latencies: list[float] = []

        async def monitor_latency() -> None:
            for _ in range(5):
                start = time.perf_counter()
                await asyncio.sleep(0.01)
                latencies.append(time.perf_counter() - start)

        def slow_run(self, cmd, timeout=600):
            time.sleep(0.05)
            return {"cmd": " ".join(cmd), "returncode": 0, "stdout": "", "stderr": ""}

        crate_analyzer.run_cargo_cmd = MethodType(slow_run, crate_analyzer)

        command_task = asyncio.create_task(
            crate_analyzer.run_cargo_cmd_async(["cargo", "check"])
        )
        await monitor_latency()
        result = await command_task

        assert result["cmd"] == "cargo check"
        assert latencies and max(latencies) < 0.05

    @pytest.mark.asyncio
    async def test_analyze_async_offloads_blocking_work(self, crate_analyzer):
        """The async analyze wrapper should delegate to a worker thread."""

        latencies: list[float] = []

        async def monitor_latency() -> None:
            for _ in range(5):
                start = time.perf_counter()
                await asyncio.sleep(0.01)
                latencies.append(time.perf_counter() - start)

        def slow_analyze(self):
            time.sleep(0.05)
            return {"status": "ok"}

        crate_analyzer.analyze = MethodType(slow_analyze, crate_analyzer)

        analyze_task = asyncio.create_task(crate_analyzer.analyze_async())
        await monitor_latency()
        result = await analyze_task

        assert result == {"status": "ok"}
        assert latencies and max(latencies) < 0.05

    @pytest.mark.asyncio
    async def test_run_cargo_cmd_with_fallback_async(self, crate_analyzer):
        """Async fallback wrapper should delegate to the sync implementation."""

        def fake_with_fallback(self, primary_cmd, fallback_cmd=None, timeout=600):
            time.sleep(0.01)
            return {
                "cmd": " ".join(primary_cmd),
                "returncode": 0,
                "used_fallback": bool(fallback_cmd),
            }

        crate_analyzer.run_cargo_cmd_with_fallback = MethodType(
            fake_with_fallback, crate_analyzer
        )

        result = await crate_analyzer.run_cargo_cmd_with_fallback_async(
            ["cargo", "build"], ["cargo", "check"]
        )

        assert result["cmd"] == "cargo build"
        assert result["used_fallback"] is True

    @pytest.mark.asyncio
    async def test_subprocess_cleanup_integration(self, crate_analyzer):
        """Test that subprocess cleanup works with CrateAnalyzer."""
        # Mock the subprocess creation to simulate cargo commands
        mock_process = Mock()
        mock_process.returncode = 0
        mock_process.communicate = AsyncMock(
            return_value=(b'{"reason": "compiler-message"}', b"")
        )
        mock_process._transport = Mock()

        with patch("asyncio.create_subprocess_exec", return_value=mock_process):
            # Test the subprocess utility directly
            results, error = await run_command_for_tests(
                ["cargo", "check"], Path(crate_analyzer.crate_source_path)
            )

            assert error is None
            assert results == [{"reason": "compiler-message"}]

            # Verify cleanup was called
            mock_process._transport.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_subprocess_cleanup_with_logger(self, crate_analyzer):
        """Test subprocess cleanup with custom logger."""
        logger = get_test_logger("test_crate_analysis")

        # Mock the subprocess creation
        mock_process = Mock()
        mock_process.returncode = 1
        mock_process.communicate = AsyncMock(return_value=(b"", b"cargo not found"))
        mock_process._transport = Mock()

        with patch("asyncio.create_subprocess_exec", return_value=mock_process):
            results, error = await run_command_for_tests(
                ["cargo", "build"], Path(crate_analyzer.crate_source_path), logger
            )

            assert error is None  # Error is logged but not returned
            assert results == []

            # Verify cleanup was called
            mock_process._transport.close.assert_called_once()
