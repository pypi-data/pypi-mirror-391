"""
Performance contract tests.

These tests verify that performance-critical code meets expected timing constraints.
These tests would have caught the sequential batch operation bug.

Critical behaviors tested:
1. Batch operations run in parallel, not sequentially
2. Async operations don't block
3. Caching provides measurable performance benefits
"""

import asyncio
import time
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

pytestmark = [pytest.mark.contract, pytest.mark.performance, pytest.mark.unit]

from azpaddypy.tools.cosmos_prompt_manager import CosmosPromptManager


class TestBatchOperationParallelism:
    """Test that batch operations are truly parallel, not sequential."""

    @pytest.mark.asyncio
    async def test_batch_async_runs_in_parallel(self):
        """
        CRITICAL: Batch operations must run in parallel using asyncio.gather().

        This test would have FAILED with the old sequential for-loop implementation.

        Expected behavior:
        - 5 operations with 0.1s delay each
        - Parallel: ~0.1s total (all run concurrently)
        - Sequential: ~0.5s total (one after another)
        """
        # Setup mock
        mock_cosmos_client = AsyncMock()
        mock_cosmos_client.get_item_async = AsyncMock()

        operation_delay = 0.1
        num_operations = 5

        # Mock get_item_async to simulate network delay
        async def mock_get_item(**kwargs):
            await asyncio.sleep(operation_delay)
            item_name = kwargs.get("item_id", "unknown")
            return {"id": item_name, "prompt_template": f"Template for {item_name}", "version": "1.0"}

        mock_cosmos_client.get_item_async.side_effect = mock_get_item

        # Create manager and execute batch operation
        manager = CosmosPromptManager(
            cosmos_client=mock_cosmos_client,
            database_name="test_db",
            container_name="test_container",
            service_name="test",
        )

        # Time the batch operation
        prompt_names = [f"prompt_{i}" for i in range(num_operations)]
        start_time = time.time()

        results = await manager.get_prompts_batch_async(prompt_names)

        duration = time.time() - start_time

        # Verify results are correct
        assert len(results) == num_operations
        assert all(name in results for name in prompt_names)

        # CRITICAL ASSERTION: Time proves parallelism
        # Parallel: ~0.1s (operations overlap)
        # Sequential: ~0.5s (operations run one by one)
        max_acceptable_duration = operation_delay * 2  # 0.2s with overhead allowance

        assert duration < max_acceptable_duration, (
            f"Batch operations appear SEQUENTIAL: took {duration:.3f}s for {num_operations} ops "
            f"with {operation_delay}s delay each. Expected <{max_acceptable_duration:.3f}s for "
            f"parallel execution. Sequential would take ~{operation_delay * num_operations:.3f}s."
        )

    @pytest.mark.asyncio
    async def test_batch_async_scales_with_operation_count(self):
        """
        Parallel operations should have roughly constant time regardless of count.

        This test verifies that increasing the number of operations doesn't
        proportionally increase execution time (as it would with sequential execution).
        """
        # Setup mock
        mock_cosmos_client = AsyncMock()

        operation_delay = 0.05

        async def mock_get_item(**kwargs):
            await asyncio.sleep(operation_delay)
            item_name = kwargs.get("item_id", "unknown")
            return {"id": item_name, "prompt_template": "template"}

        mock_cosmos_client.get_item_async.side_effect = mock_get_item

        manager = CosmosPromptManager(
            cosmos_client=mock_cosmos_client,
            database_name="test_db",
            container_name="test_container",
            service_name="test",
        )

        # Test with different batch sizes
        timing_results = {}

        for batch_size in [5, 10, 20]:
            prompt_names = [f"prompt_{i}" for i in range(batch_size)]

            start_time = time.time()
            await manager.get_prompts_batch_async(prompt_names)
            duration = time.time() - start_time

            timing_results[batch_size] = duration

        # With parallel execution, all batches should complete in similar time
        # (slightly more for larger batches due to overhead, but not proportional)
        time_5 = timing_results[5]
        time_20 = timing_results[20]

        # If operations were sequential, time_20 would be ~4x time_5
        # With parallel execution, time_20 should be < 2x time_5
        assert time_20 < time_5 * 2.5, (
            f"Operations appear sequential: 20-item batch took {time_20:.3f}s vs "
            f"5-item batch {time_5:.3f}s (ratio: {time_20 / time_5:.2f}x). "
            f"Expected <2.5x for parallel execution."
        )


class TestAsyncPerformance:
    """Test that async code doesn't block the event loop."""

    @pytest.mark.asyncio
    async def test_async_sleep_not_blocking(self):
        """
        Verify that async sleep doesn't block other coroutines.

        This ensures we're using asyncio.sleep() not time.sleep().
        """
        results = []

        async def task_with_sleep(task_id, delay):
            await asyncio.sleep(delay)
            results.append(task_id)

        # Start tasks with different delays
        start_time = time.time()
        await asyncio.gather(
            task_with_sleep(1, 0.1),
            task_with_sleep(2, 0.05),
            task_with_sleep(3, 0.15),
        )
        duration = time.time() - start_time

        # Should complete in ~0.15s (longest task), not 0.3s (sum of all)
        assert duration < 0.25, f"Tasks appear to be blocking: took {duration:.3f}s, expected <0.25s"

        # Tasks should complete in order of delay (shortest first)
        assert results == [2, 1, 3], f"Tasks completed in wrong order: {results}, expected [2, 1, 3]"


class TestCachingPerformance:
    """Test that caching provides measurable performance benefits."""

    @patch("azpaddypy.resources.storage.BlobServiceClient")
    def test_cache_provides_measurable_speedup(self, mock_blob_client):
        """
        Verify that cached instances are returned faster than creating new ones.

        This is a behavioral test: caching should be faster than recreation.
        """
        from _test_utils import create_mock_credential

        from azpaddypy.resources.storage import create_azure_storage

        mock_blob_client.return_value = MagicMock()
        cred = create_mock_credential()
        url = "https://testaccount.blob.core.windows.net"

        # First call: creates instance (slower)
        start_first = time.perf_counter()
        create_azure_storage(account_url=url, credential=cred, service_name="test")
        first_duration = time.perf_counter() - start_first

        # Subsequent calls: hit cache (faster)
        cache_durations = []
        for _ in range(100):
            start_cached = time.perf_counter()
            create_azure_storage(account_url=url, credential=cred, service_name="test")
            cache_durations.append(time.perf_counter() - start_cached)

        avg_cache_duration = sum(cache_durations) / len(cache_durations)

        # Cached calls should be significantly faster
        # (This is a loose assertion; main goal is to verify caching works)
        assert avg_cache_duration < first_duration, (
            f"Cache doesn't appear to provide speedup: first call {first_duration:.6f}s, "
            f"avg cached call {avg_cache_duration:.6f}s"
        )


class TestPerformanceRegressionGuards:
    """Guard rails to catch performance regressions."""

    @pytest.mark.asyncio
    async def test_batch_operation_overhead_is_acceptable(self):
        """
        Verify that batch operation overhead is minimal.

        Overhead should be <50ms for typical batch sizes.
        """
        # Setup fast mock (no artificial delay)
        mock_cosmos_client = AsyncMock()

        async def instant_response(**kwargs):
            return {"id": kwargs.get("item_id"), "prompt_template": "template"}

        mock_cosmos_client.get_item_async.side_effect = instant_response

        manager = CosmosPromptManager(
            cosmos_client=mock_cosmos_client,
            database_name="test_db",
            container_name="test_container",
            service_name="test",
        )

        # Measure overhead for batch operation
        prompt_names = [f"prompt_{i}" for i in range(10)]

        start_time = time.perf_counter()
        await manager.get_prompts_batch_async(prompt_names)
        duration = time.perf_counter() - start_time

        # With instant responses, overhead should be minimal
        max_acceptable_overhead = 0.05  # 50ms

        assert duration < max_acceptable_overhead, (
            f"Batch operation overhead too high: {duration:.3f}s for {len(prompt_names)} items. "
            f"Expected <{max_acceptable_overhead}s with instant responses."
        )
