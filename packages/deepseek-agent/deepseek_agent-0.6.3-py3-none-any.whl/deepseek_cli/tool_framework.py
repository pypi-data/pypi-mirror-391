"""Enhanced tool execution framework with robust error handling and validation."""

from __future__ import annotations

import asyncio
import functools
import inspect
import json
import logging
import time
import traceback
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import (
    Any,
    Callable,
    Dict,
    List,
    Optional,
    Set,
    Tuple,
    Type,
    TypeVar,
    Union,
)

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

# Set up logging
logger = logging.getLogger(__name__)

T = TypeVar("T")
ToolFunc = TypeVar("ToolFunc", bound=Callable[..., Any])


class ToolStatus(Enum):
    """Status of tool execution."""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"


class ToolPriority(Enum):
    """Priority levels for tool execution."""
    LOW = 1
    NORMAL = 5
    HIGH = 10
    CRITICAL = 20


@dataclass
class ToolMetadata:
    """Metadata for a tool."""
    name: str
    category: str
    description: str
    parameters: Dict[str, Any]
    returns: str
    examples: List[str] = field(default_factory=list)
    tags: Set[str] = field(default_factory=set)
    priority: ToolPriority = ToolPriority.NORMAL
    timeout: Optional[float] = None
    requires_confirmation: bool = False
    cacheable: bool = False
    parallel_safe: bool = True


@dataclass
class ToolResult:
    """Result of tool execution with detailed metadata."""
    status: ToolStatus
    output: Any
    error: Optional[str] = None
    execution_time: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    traceback: Optional[str] = None

    @property
    def is_success(self) -> bool:
        return self.status == ToolStatus.SUCCESS

    @property
    def is_error(self) -> bool:
        return self.status in (ToolStatus.FAILED, ToolStatus.TIMEOUT, ToolStatus.CANCELLED)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "status": self.status.value,
            "output": self.output,
            "error": self.error,
            "execution_time": self.execution_time,
            "metadata": self.metadata,
            "traceback": self.traceback,
        }


class ToolValidator:
    """Validates tool inputs and outputs."""

    @staticmethod
    def validate_parameters(
        params: Dict[str, Any],
        schema: Dict[str, Any]
    ) -> Tuple[bool, Optional[str]]:
        """Validate parameters against a schema."""
        required = schema.get("required", [])
        properties = schema.get("properties", {})

        # Check required parameters
        for req in required:
            if req not in params:
                return False, f"Missing required parameter: {req}"

        # Validate parameter types
        for key, value in params.items():
            if key not in properties:
                continue

            prop_schema = properties[key]
            expected_type = prop_schema.get("type")

            if not ToolValidator._check_type(value, expected_type):
                return False, f"Parameter '{key}' has wrong type. Expected: {expected_type}"

        return True, None

    @staticmethod
    def _check_type(value: Any, expected: str) -> bool:
        """Check if value matches expected type."""
        type_map = {
            "string": str,
            "integer": int,
            "number": (int, float),
            "boolean": bool,
            "array": list,
            "object": dict,
        }

        if expected not in type_map:
            return True

        expected_type = type_map[expected]
        return isinstance(value, expected_type)


class ToolCache:
    """Simple caching system for tool results."""

    def __init__(self, max_size: int = 100, ttl: float = 300):
        self._cache: Dict[str, Tuple[Any, float]] = {}
        self._max_size = max_size
        self._ttl = ttl

    def get(self, key: str) -> Optional[Any]:
        """Get cached result if available and not expired."""
        if key not in self._cache:
            return None

        value, timestamp = self._cache[key]
        if time.time() - timestamp > self._ttl:
            del self._cache[key]
            return None

        return value

    def set(self, key: str, value: Any) -> None:
        """Cache a result."""
        # Simple LRU: remove oldest if at capacity
        if len(self._cache) >= self._max_size:
            oldest = min(self._cache.items(), key=lambda x: x[1][1])
            del self._cache[oldest[0]]

        self._cache[key] = (value, time.time())

    def clear(self) -> None:
        """Clear all cached results."""
        self._cache.clear()


class BaseTool(ABC):
    """Abstract base class for all tools."""

    def __init__(self, metadata: ToolMetadata):
        self.metadata = metadata
        self._cache = ToolCache() if metadata.cacheable else None
        self._execution_count = 0
        self._total_execution_time = 0.0

    @abstractmethod
    async def execute_async(self, **kwargs) -> Any:
        """Execute the tool asynchronously."""
        pass

    def execute(self, **kwargs) -> Any:
        """Execute the tool synchronously."""
        return asyncio.run(self.execute_async(**kwargs))

    def get_cache_key(self, **kwargs) -> str:
        """Generate cache key from parameters."""
        return json.dumps(kwargs, sort_keys=True)

    async def __call__(self, **kwargs) -> ToolResult:
        """Execute tool with error handling and metadata."""
        start_time = time.time()

        try:
            # Check cache if enabled
            if self._cache:
                cache_key = self.get_cache_key(**kwargs)
                cached = self._cache.get(cache_key)
                if cached is not None:
                    return ToolResult(
                        status=ToolStatus.SUCCESS,
                        output=cached,
                        execution_time=0.0,
                        metadata={"cached": True}
                    )

            # Validate parameters
            valid, error = ToolValidator.validate_parameters(
                kwargs, self.metadata.parameters
            )
            if not valid:
                return ToolResult(
                    status=ToolStatus.FAILED,
                    output=None,
                    error=error,
                    execution_time=time.time() - start_time
                )

            # Execute with timeout if specified
            if self.metadata.timeout:
                result = await asyncio.wait_for(
                    self.execute_async(**kwargs),
                    timeout=self.metadata.timeout
                )
            else:
                result = await self.execute_async(**kwargs)

            # Cache result if enabled
            if self._cache:
                self._cache.set(cache_key, result)

            # Update statistics
            self._execution_count += 1
            execution_time = time.time() - start_time
            self._total_execution_time += execution_time

            return ToolResult(
                status=ToolStatus.SUCCESS,
                output=result,
                execution_time=execution_time,
                metadata={
                    "execution_count": self._execution_count,
                    "average_time": self._total_execution_time / self._execution_count
                }
            )

        except asyncio.TimeoutError:
            return ToolResult(
                status=ToolStatus.TIMEOUT,
                output=None,
                error=f"Tool execution timed out after {self.metadata.timeout} seconds",
                execution_time=time.time() - start_time
            )
        except Exception as e:
            return ToolResult(
                status=ToolStatus.FAILED,
                output=None,
                error=str(e),
                execution_time=time.time() - start_time,
                traceback=traceback.format_exc()
            )


class ToolRegistry:
    """Registry for managing tools."""

    def __init__(self):
        self._tools: Dict[str, BaseTool] = {}
        self._categories: Dict[str, Set[str]] = {}
        self._tags: Dict[str, Set[str]] = {}

    def register(self, tool: BaseTool) -> None:
        """Register a tool."""
        name = tool.metadata.name
        if name in self._tools:
            raise ValueError(f"Tool '{name}' already registered")

        self._tools[name] = tool

        # Update category index
        category = tool.metadata.category
        if category not in self._categories:
            self._categories[category] = set()
        self._categories[category].add(name)

        # Update tag index
        for tag in tool.metadata.tags:
            if tag not in self._tags:
                self._tags[tag] = set()
            self._tags[tag].add(name)

    def get(self, name: str) -> Optional[BaseTool]:
        """Get a tool by name."""
        return self._tools.get(name)

    def get_by_category(self, category: str) -> List[BaseTool]:
        """Get all tools in a category."""
        names = self._categories.get(category, set())
        return [self._tools[name] for name in names]

    def get_by_tag(self, tag: str) -> List[BaseTool]:
        """Get all tools with a specific tag."""
        names = self._tags.get(tag, set())
        return [self._tools[name] for name in names]

    def list_all(self) -> List[str]:
        """List all registered tool names."""
        return list(self._tools.keys())

    def get_metadata(self) -> Dict[str, ToolMetadata]:
        """Get metadata for all tools."""
        return {name: tool.metadata for name, tool in self._tools.items()}


class ParallelToolExecutor:
    """Executes multiple tools in parallel with dependency management."""

    def __init__(self, registry: ToolRegistry):
        self.registry = registry
        self.console = Console()

    async def execute_parallel(
        self,
        tasks: List[Dict[str, Any]],
        max_concurrent: int = 5
    ) -> List[ToolResult]:
        """Execute multiple tools in parallel."""
        semaphore = asyncio.Semaphore(max_concurrent)

        async def run_tool(task: Dict[str, Any]) -> ToolResult:
            async with semaphore:
                tool_name = task.get("tool")
                params = task.get("params", {})

                tool = self.registry.get(tool_name)
                if not tool:
                    return ToolResult(
                        status=ToolStatus.FAILED,
                        output=None,
                        error=f"Tool '{tool_name}' not found"
                    )

                if not tool.metadata.parallel_safe:
                    # Wait for sequential execution
                    await asyncio.sleep(0.1)

                return await tool(**params)

        results = await asyncio.gather(
            *[run_tool(task) for task in tasks],
            return_exceptions=True
        )

        # Convert exceptions to ToolResult
        final_results = []
        for result in results:
            if isinstance(result, Exception):
                final_results.append(ToolResult(
                    status=ToolStatus.FAILED,
                    output=None,
                    error=str(result),
                    traceback=traceback.format_exception(type(result), result, result.__traceback__)
                ))
            else:
                final_results.append(result)

        return final_results

    def execute_with_dependencies(
        self,
        tasks: List[Dict[str, Any]],
        dependencies: Dict[int, List[int]]
    ) -> List[ToolResult]:
        """Execute tools with dependency management."""
        # This is a simplified version - a full implementation would use a DAG
        return asyncio.run(self.execute_parallel(tasks))


class ToolMonitor:
    """Monitors tool execution and provides statistics."""

    def __init__(self):
        self.executions: List[Dict[str, Any]] = []
        self.start_time = time.time()

    def record_execution(
        self,
        tool_name: str,
        result: ToolResult,
        params: Dict[str, Any]
    ) -> None:
        """Record a tool execution."""
        self.executions.append({
            "timestamp": time.time(),
            "tool": tool_name,
            "status": result.status.value,
            "execution_time": result.execution_time,
            "params": params,
            "error": result.error
        })

    def get_statistics(self) -> Dict[str, Any]:
        """Get execution statistics."""
        if not self.executions:
            return {}

        total_time = sum(e["execution_time"] for e in self.executions)
        success_count = sum(1 for e in self.executions if e["status"] == "success")
        error_count = sum(1 for e in self.executions if e["status"] in ("failed", "timeout"))

        tool_stats = {}
        for exec_data in self.executions:
            tool = exec_data["tool"]
            if tool not in tool_stats:
                tool_stats[tool] = {"count": 0, "total_time": 0, "errors": 0}
            tool_stats[tool]["count"] += 1
            tool_stats[tool]["total_time"] += exec_data["execution_time"]
            if exec_data["status"] in ("failed", "timeout"):
                tool_stats[tool]["errors"] += 1

        return {
            "total_executions": len(self.executions),
            "success_rate": success_count / len(self.executions) if self.executions else 0,
            "error_rate": error_count / len(self.executions) if self.executions else 0,
            "total_execution_time": total_time,
            "average_execution_time": total_time / len(self.executions) if self.executions else 0,
            "uptime": time.time() - self.start_time,
            "tool_statistics": tool_stats
        }

    def display_statistics(self) -> None:
        """Display statistics in a formatted table."""
        stats = self.get_statistics()
        if not stats:
            print("No executions recorded yet.")
            return

        console = Console()

        # Overall statistics
        overall_table = Table(title="Overall Statistics", show_header=True)
        overall_table.add_column("Metric", style="cyan")
        overall_table.add_column("Value", style="green")

        overall_table.add_row("Total Executions", str(stats["total_executions"]))
        overall_table.add_row("Success Rate", f"{stats['success_rate']:.1%}")
        overall_table.add_row("Error Rate", f"{stats['error_rate']:.1%}")
        overall_table.add_row("Total Time", f"{stats['total_execution_time']:.2f}s")
        overall_table.add_row("Average Time", f"{stats['average_execution_time']:.2f}s")
        overall_table.add_row("Uptime", f"{stats['uptime']:.0f}s")

        console.print(overall_table)

        # Per-tool statistics
        if stats.get("tool_statistics"):
            tool_table = Table(title="Tool Statistics", show_header=True)
            tool_table.add_column("Tool", style="cyan")
            tool_table.add_column("Executions", style="yellow")
            tool_table.add_column("Total Time", style="green")
            tool_table.add_column("Avg Time", style="green")
            tool_table.add_column("Errors", style="red")

            for tool, tool_stats in stats["tool_statistics"].items():
                avg_time = tool_stats["total_time"] / tool_stats["count"]
                tool_table.add_row(
                    tool,
                    str(tool_stats["count"]),
                    f"{tool_stats['total_time']:.2f}s",
                    f"{avg_time:.2f}s",
                    str(tool_stats["errors"])
                )

            console.print(tool_table)


# Error recovery decorator
def with_retry(max_attempts: int = 3, delay: float = 1.0, backoff: float = 2.0):
    """Decorator to add retry logic to tool execution."""
    def decorator(func: ToolFunc) -> ToolFunc:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            attempt = 0
            current_delay = delay

            while attempt < max_attempts:
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    attempt += 1
                    if attempt >= max_attempts:
                        raise

                    logger.warning(
                        f"Attempt {attempt} failed for {func.__name__}: {e}. "
                        f"Retrying in {current_delay}s..."
                    )
                    await asyncio.sleep(current_delay)
                    current_delay *= backoff

        return wrapper
    return decorator


# Circuit breaker pattern
class CircuitBreaker:
    """Circuit breaker for preventing cascading failures."""

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: float = 60.0,
        expected_exception: Type[Exception] = Exception
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        self.failure_count = 0
        self.last_failure_time: Optional[float] = None
        self.state = "closed"  # closed, open, half_open

    def call(self, func: Callable, *args, **kwargs) -> Any:
        """Call function through circuit breaker."""
        if self.state == "open":
            if self.last_failure_time and \
               time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = "half_open"
            else:
                raise Exception(f"Circuit breaker is open for {func.__name__}")

        try:
            result = func(*args, **kwargs)
            if self.state == "half_open":
                self.state = "closed"
                self.failure_count = 0
            return result
        except self.expected_exception as e:
            self.failure_count += 1
            self.last_failure_time = time.time()

            if self.failure_count >= self.failure_threshold:
                self.state = "open"
                logger.error(f"Circuit breaker opened for {func.__name__}")

            raise


def create_enhanced_tool(
    name: str,
    category: str,
    description: str,
    func: Callable,
    **metadata_kwargs
) -> BaseTool:
    """Factory function to create tools from regular functions."""

    class DynamicTool(BaseTool):
        async def execute_async(self, **kwargs):
            if asyncio.iscoroutinefunction(func):
                return await func(**kwargs)
            else:
                return func(**kwargs)

    # Extract parameter information from function signature
    sig = inspect.signature(func)
    parameters = {
        "type": "object",
        "properties": {},
        "required": []
    }

    for param_name, param in sig.parameters.items():
        if param_name == "self":
            continue

        param_info = {"type": "string"}  # Default type
        if param.annotation != inspect.Parameter.empty:
            # Try to infer type from annotation
            if param.annotation == str:
                param_info["type"] = "string"
            elif param.annotation == int:
                param_info["type"] = "integer"
            elif param.annotation == float:
                param_info["type"] = "number"
            elif param.annotation == bool:
                param_info["type"] = "boolean"
            elif param.annotation == list:
                param_info["type"] = "array"
            elif param.annotation == dict:
                param_info["type"] = "object"

        parameters["properties"][param_name] = param_info

        if param.default == inspect.Parameter.empty:
            parameters["required"].append(param_name)

    metadata = ToolMetadata(
        name=name,
        category=category,
        description=description,
        parameters=parameters,
        returns=str(sig.return_annotation) if sig.return_annotation != inspect.Parameter.empty else "Any",
        **metadata_kwargs
    )

    return DynamicTool(metadata)