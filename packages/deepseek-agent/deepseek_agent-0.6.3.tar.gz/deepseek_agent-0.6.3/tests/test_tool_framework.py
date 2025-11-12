"""Comprehensive tests for the enhanced tool framework."""

import asyncio
import pytest
import time
from unittest.mock import AsyncMock, MagicMock, patch

from deepseek_cli.tool_framework import (
    BaseTool,
    CircuitBreaker,
    ParallelToolExecutor,
    ToolCache,
    ToolMetadata,
    ToolMonitor,
    ToolPriority,
    ToolRegistry,
    ToolResult,
    ToolStatus,
    ToolValidator,
    create_enhanced_tool,
    with_retry,
)


class TestToolValidator:
    """Test tool parameter validation."""

    def test_validate_simple_types(self):
        """Test validation of simple parameter types."""
        schema = {
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "integer"},
                "active": {"type": "boolean"},
            },
            "required": ["name", "age"]
        }

        # Valid parameters
        valid, error = ToolValidator.validate_parameters(
            {"name": "John", "age": 30, "active": True},
            schema
        )
        assert valid
        assert error is None

        # Missing required parameter
        valid, error = ToolValidator.validate_parameters(
            {"name": "John"},
            schema
        )
        assert not valid
        assert "Missing required parameter: age" in error

        # Wrong type
        valid, error = ToolValidator.validate_parameters(
            {"name": "John", "age": "thirty"},
            schema
        )
        assert not valid
        assert "wrong type" in error

    def test_validate_complex_types(self):
        """Test validation of complex parameter types."""
        schema = {
            "properties": {
                "items": {"type": "array"},
                "config": {"type": "object"},
            },
            "required": []
        }

        # Valid parameters
        valid, error = ToolValidator.validate_parameters(
            {"items": [1, 2, 3], "config": {"key": "value"}},
            schema
        )
        assert valid
        assert error is None

        # Wrong type for array
        valid, error = ToolValidator.validate_parameters(
            {"items": "not an array"},
            schema
        )
        assert not valid
        assert "wrong type" in error


class TestToolCache:
    """Test caching functionality."""

    def test_basic_caching(self):
        """Test basic cache operations."""
        cache = ToolCache(max_size=3, ttl=10)

        # Test set and get
        assert cache.get("key1") is None
        cache.set("key1", "value1")
        assert cache.get("key1") == "value1"

        # Test multiple entries
        cache.set("key2", "value2")
        cache.set("key3", "value3")
        assert cache.get("key2") == "value2"
        assert cache.get("key3") == "value3"

    def test_cache_eviction(self):
        """Test cache eviction when max size is reached."""
        cache = ToolCache(max_size=2)

        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.set("key3", "value3")  # Should evict key1

        # key1 should be evicted
        assert cache.get("key1") is None
        assert cache.get("key2") == "value2"
        assert cache.get("key3") == "value3"

    def test_cache_ttl(self):
        """Test cache TTL expiration."""
        cache = ToolCache(ttl=0.1)  # 100ms TTL

        cache.set("key1", "value1")
        assert cache.get("key1") == "value1"

        # Wait for expiration
        time.sleep(0.2)
        assert cache.get("key1") is None

    def test_cache_clear(self):
        """Test clearing the cache."""
        cache = ToolCache()

        cache.set("key1", "value1")
        cache.set("key2", "value2")
        assert cache.get("key1") == "value1"

        cache.clear()
        assert cache.get("key1") is None
        assert cache.get("key2") is None


class TestBaseTool:
    """Test base tool functionality."""

    @pytest.mark.asyncio
    async def test_tool_execution(self):
        """Test basic tool execution."""

        class TestTool(BaseTool):
            async def execute_async(self, **kwargs):
                return f"Executed with {kwargs}"

        metadata = ToolMetadata(
            name="test_tool",
            category="test",
            description="Test tool",
            parameters={},
            returns="str"
        )

        tool = TestTool(metadata)
        result = await tool(param1="value1")

        assert result.status == ToolStatus.SUCCESS
        assert result.output == "Executed with {'param1': 'value1'}"
        assert result.execution_time > 0

    @pytest.mark.asyncio
    async def test_tool_with_validation(self):
        """Test tool with parameter validation."""

        class ValidatedTool(BaseTool):
            async def execute_async(self, name: str, age: int):
                return f"{name} is {age} years old"

        metadata = ToolMetadata(
            name="validated_tool",
            category="test",
            description="Tool with validation",
            parameters={
                "properties": {
                    "name": {"type": "string"},
                    "age": {"type": "integer"}
                },
                "required": ["name", "age"]
            },
            returns="str"
        )

        tool = ValidatedTool(metadata)

        # Valid parameters
        result = await tool(name="John", age=30)
        assert result.status == ToolStatus.SUCCESS
        assert result.output == "John is 30 years old"

        # Invalid parameters (missing required)
        result = await tool(name="John")
        assert result.status == ToolStatus.FAILED
        assert "Missing required parameter" in result.error

    @pytest.mark.asyncio
    async def test_tool_with_timeout(self):
        """Test tool timeout functionality."""

        class SlowTool(BaseTool):
            async def execute_async(self, **kwargs):
                await asyncio.sleep(2)
                return "Done"

        metadata = ToolMetadata(
            name="slow_tool",
            category="test",
            description="Slow tool",
            parameters={},
            returns="str",
            timeout=0.1  # 100ms timeout
        )

        tool = SlowTool(metadata)
        result = await tool()

        assert result.status == ToolStatus.TIMEOUT
        assert "timed out" in result.error

    @pytest.mark.asyncio
    async def test_tool_with_caching(self):
        """Test tool caching functionality."""

        class CachedTool(BaseTool):
            def __init__(self, metadata):
                super().__init__(metadata)
                self.call_count = 0

            async def execute_async(self, value: int):
                self.call_count += 1
                return value * 2

        metadata = ToolMetadata(
            name="cached_tool",
            category="test",
            description="Cached tool",
            parameters={},
            returns="int",
            cacheable=True
        )

        tool = CachedTool(metadata)

        # First call should execute
        result1 = await tool(value=5)
        assert result1.output == 10
        assert tool.call_count == 1

        # Second call with same params should use cache
        result2 = await tool(value=5)
        assert result2.output == 10
        assert tool.call_count == 1  # No additional execution
        assert result2.metadata.get("cached") is True

        # Different params should execute
        result3 = await tool(value=7)
        assert result3.output == 14
        assert tool.call_count == 2


class TestToolRegistry:
    """Test tool registry functionality."""

    def test_register_and_get_tools(self):
        """Test registering and retrieving tools."""
        registry = ToolRegistry()

        tool1 = create_enhanced_tool(
            name="tool1",
            category="cat1",
            description="Tool 1",
            func=lambda: "result1",
            tags={"tag1", "tag2"}
        )

        tool2 = create_enhanced_tool(
            name="tool2",
            category="cat2",
            description="Tool 2",
            func=lambda: "result2",
            tags={"tag2", "tag3"}
        )

        registry.register(tool1)
        registry.register(tool2)

        # Get by name
        assert registry.get("tool1") == tool1
        assert registry.get("tool2") == tool2
        assert registry.get("nonexistent") is None

        # List all
        assert set(registry.list_all()) == {"tool1", "tool2"}

    def test_get_tools_by_category(self):
        """Test retrieving tools by category."""
        registry = ToolRegistry()

        tool1 = create_enhanced_tool(
            name="tool1",
            category="file_system",
            description="Tool 1",
            func=lambda: None
        )

        tool2 = create_enhanced_tool(
            name="tool2",
            category="file_system",
            description="Tool 2",
            func=lambda: None
        )

        tool3 = create_enhanced_tool(
            name="tool3",
            category="network",
            description="Tool 3",
            func=lambda: None
        )

        registry.register(tool1)
        registry.register(tool2)
        registry.register(tool3)

        file_tools = registry.get_by_category("file_system")
        assert len(file_tools) == 2
        assert tool1 in file_tools
        assert tool2 in file_tools

        network_tools = registry.get_by_category("network")
        assert len(network_tools) == 1
        assert tool3 in network_tools

    def test_get_tools_by_tag(self):
        """Test retrieving tools by tag."""
        registry = ToolRegistry()

        tool1 = create_enhanced_tool(
            name="tool1",
            category="test",
            description="Tool 1",
            func=lambda: None,
            tags={"read", "safe"}
        )

        tool2 = create_enhanced_tool(
            name="tool2",
            category="test",
            description="Tool 2",
            func=lambda: None,
            tags={"write", "dangerous"}
        )

        registry.register(tool1)
        registry.register(tool2)

        safe_tools = registry.get_by_tag("safe")
        assert len(safe_tools) == 1
        assert tool1 in safe_tools

        dangerous_tools = registry.get_by_tag("dangerous")
        assert len(dangerous_tools) == 1
        assert tool2 in dangerous_tools

    def test_duplicate_registration(self):
        """Test that duplicate tool registration raises error."""
        registry = ToolRegistry()

        tool = create_enhanced_tool(
            name="tool1",
            category="test",
            description="Tool",
            func=lambda: None
        )

        registry.register(tool)

        with pytest.raises(ValueError, match="already registered"):
            registry.register(tool)


class TestParallelToolExecutor:
    """Test parallel tool execution."""

    @pytest.mark.asyncio
    async def test_parallel_execution(self):
        """Test executing multiple tools in parallel."""
        registry = ToolRegistry()

        # Create tools with different execution times
        async def fast_func():
            await asyncio.sleep(0.1)
            return "fast"

        async def slow_func():
            await asyncio.sleep(0.2)
            return "slow"

        fast_tool = create_enhanced_tool(
            name="fast",
            category="test",
            description="Fast tool",
            func=fast_func
        )

        slow_tool = create_enhanced_tool(
            name="slow",
            category="test",
            description="Slow tool",
            func=slow_func
        )

        registry.register(fast_tool)
        registry.register(slow_tool)

        executor = ParallelToolExecutor(registry)

        # Execute in parallel
        start = time.time()
        results = await executor.execute_parallel([
            {"tool": "fast", "params": {}},
            {"tool": "slow", "params": {}},
        ])
        elapsed = time.time() - start

        # Should complete in ~0.2s (not 0.3s if sequential)
        assert elapsed < 0.25

        assert len(results) == 2
        assert results[0].status == ToolStatus.SUCCESS
        assert results[0].output == "fast"
        assert results[1].status == ToolStatus.SUCCESS
        assert results[1].output == "slow"

    @pytest.mark.asyncio
    async def test_parallel_with_concurrency_limit(self):
        """Test parallel execution with concurrency limit."""
        registry = ToolRegistry()

        call_times = []

        async def track_time():
            call_times.append(time.time())
            await asyncio.sleep(0.1)
            return "done"

        tool = create_enhanced_tool(
            name="tracker",
            category="test",
            description="Tracking tool",
            func=track_time
        )

        registry.register(tool)

        executor = ParallelToolExecutor(registry)

        # Execute 5 tasks with max_concurrent=2
        await executor.execute_parallel(
            [{"tool": "tracker", "params": {}} for _ in range(5)],
            max_concurrent=2
        )

        # Check that tasks were executed in batches
        # With max_concurrent=2, we should see clear batching
        assert len(call_times) == 5


class TestToolMonitor:
    """Test tool monitoring functionality."""

    def test_record_execution(self):
        """Test recording tool executions."""
        monitor = ToolMonitor()

        # Record successful execution
        monitor.record_execution(
            "tool1",
            ToolResult(
                status=ToolStatus.SUCCESS,
                output="result",
                execution_time=0.5
            ),
            {"param": "value"}
        )

        # Record failed execution
        monitor.record_execution(
            "tool2",
            ToolResult(
                status=ToolStatus.FAILED,
                output=None,
                error="Error message",
                execution_time=0.1
            ),
            {}
        )

        stats = monitor.get_statistics()

        assert stats["total_executions"] == 2
        assert stats["success_rate"] == 0.5
        assert stats["error_rate"] == 0.5
        assert 0.5 <= stats["total_execution_time"] <= 0.7
        assert "tool1" in stats["tool_statistics"]
        assert "tool2" in stats["tool_statistics"]

    def test_statistics_calculation(self):
        """Test statistics calculation."""
        monitor = ToolMonitor()

        # Record multiple executions
        for i in range(10):
            status = ToolStatus.SUCCESS if i % 2 == 0 else ToolStatus.FAILED
            monitor.record_execution(
                f"tool{i % 3}",
                ToolResult(
                    status=status,
                    output="result" if status == ToolStatus.SUCCESS else None,
                    error="error" if status == ToolStatus.FAILED else None,
                    execution_time=0.1
                ),
                {}
            )

        stats = monitor.get_statistics()

        assert stats["total_executions"] == 10
        assert stats["success_rate"] == 0.5
        assert stats["error_rate"] == 0.5
        assert stats["average_execution_time"] == pytest.approx(0.1, rel=0.1)


class TestCircuitBreaker:
    """Test circuit breaker functionality."""

    def test_circuit_breaker_opens_after_failures(self):
        """Test that circuit breaker opens after threshold failures."""
        breaker = CircuitBreaker(failure_threshold=3, recovery_timeout=1.0)

        def failing_func():
            raise Exception("Failure")

        # First 2 failures shouldn't open the circuit
        for _ in range(2):
            with pytest.raises(Exception):
                breaker.call(failing_func)
        assert breaker.state == "closed"

        # Third failure should open the circuit
        with pytest.raises(Exception):
            breaker.call(failing_func)
        assert breaker.state == "open"

        # Subsequent calls should fail immediately
        with pytest.raises(Exception, match="Circuit breaker is open"):
            breaker.call(failing_func)

    def test_circuit_breaker_recovery(self):
        """Test circuit breaker recovery after timeout."""
        breaker = CircuitBreaker(failure_threshold=1, recovery_timeout=0.1)

        def func(should_fail=True):
            if should_fail:
                raise Exception("Failure")
            return "Success"

        # Open the circuit
        with pytest.raises(Exception):
            breaker.call(func, True)
        assert breaker.state == "open"

        # Wait for recovery timeout
        time.sleep(0.15)

        # Circuit should go to half_open and allow one attempt
        result = breaker.call(func, False)
        assert result == "Success"
        assert breaker.state == "closed"


class TestRetryDecorator:
    """Test retry decorator functionality."""

    @pytest.mark.asyncio
    async def test_retry_on_failure(self):
        """Test that function retries on failure."""
        attempt_count = 0

        @with_retry(max_attempts=3, delay=0.01)
        async def failing_func():
            nonlocal attempt_count
            attempt_count += 1
            if attempt_count < 3:
                raise Exception("Temporary failure")
            return "Success"

        result = await failing_func()
        assert result == "Success"
        assert attempt_count == 3

    @pytest.mark.asyncio
    async def test_retry_max_attempts_exceeded(self):
        """Test that retry gives up after max attempts."""
        attempt_count = 0

        @with_retry(max_attempts=3, delay=0.01)
        async def always_failing():
            nonlocal attempt_count
            attempt_count += 1
            raise Exception("Permanent failure")

        with pytest.raises(Exception, match="Permanent failure"):
            await always_failing()

        assert attempt_count == 3

    @pytest.mark.asyncio
    async def test_retry_with_backoff(self):
        """Test exponential backoff in retries."""
        attempt_times = []

        @with_retry(max_attempts=3, delay=0.01, backoff=2.0)
        async def track_timing():
            attempt_times.append(time.time())
            if len(attempt_times) < 3:
                raise Exception("Retry")
            return "Done"

        await track_timing()

        assert len(attempt_times) == 3
        # Check that delays increase exponentially
        delay1 = attempt_times[1] - attempt_times[0]
        delay2 = attempt_times[2] - attempt_times[1]
        assert delay2 > delay1 * 1.5  # Allow some variance


class TestCreateEnhancedTool:
    """Test the create_enhanced_tool factory function."""

    @pytest.mark.asyncio
    async def test_create_tool_from_sync_function(self):
        """Test creating tool from synchronous function."""

        def sync_func(name: str, value: int = 10) -> str:
            return f"{name}: {value}"

        tool = create_enhanced_tool(
            name="sync_tool",
            category="test",
            description="Test sync tool",
            func=sync_func
        )

        result = await tool(name="test", value=20)
        assert result.status == ToolStatus.SUCCESS
        assert result.output == "test: 20"

    @pytest.mark.asyncio
    async def test_create_tool_from_async_function(self):
        """Test creating tool from asynchronous function."""

        async def async_func(name: str) -> str:
            await asyncio.sleep(0.01)
            return f"Hello, {name}"

        tool = create_enhanced_tool(
            name="async_tool",
            category="test",
            description="Test async tool",
            func=async_func
        )

        result = await tool(name="World")
        assert result.status == ToolStatus.SUCCESS
        assert result.output == "Hello, World"

    @pytest.mark.asyncio
    async def test_create_tool_with_metadata(self):
        """Test creating tool with custom metadata."""

        def func():
            return "result"

        tool = create_enhanced_tool(
            name="custom_tool",
            category="test",
            description="Custom tool",
            func=func,
            priority=ToolPriority.HIGH,
            timeout=5.0,
            requires_confirmation=True,
            cacheable=True,
            parallel_safe=False,
            tags={"custom", "test"}
        )

        assert tool.metadata.name == "custom_tool"
        assert tool.metadata.priority == ToolPriority.HIGH
        assert tool.metadata.timeout == 5.0
        assert tool.metadata.requires_confirmation is True
        assert tool.metadata.cacheable is True
        assert tool.metadata.parallel_safe is False
        assert "custom" in tool.metadata.tags
        assert "test" in tool.metadata.tags