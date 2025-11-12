"""Integration module that combines all enhancements into a unified agent system."""

from __future__ import annotations

import asyncio
import json
import logging
import os
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from openai import OpenAI
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from .agent import AgentOptions, ExecutionMode, ToolExecutor
from .enhanced_agent import (
    EnhancedAgentOrchestrator,
    EnhancedToolExecutor,
    ExecutionContext,
)
from .performance import (
    AdvancedCache,
    BatchProcessor,
    CacheStrategy,
    ConnectionPool,
    DiskCache,
    RateLimiter,
    memoize,
    profile_performance,
)
from .tool_framework import (
    BaseTool,
    ParallelToolExecutor,
    ToolMonitor,
    ToolRegistry,
    ToolResult,
    create_enhanced_tool,
)
from .validation import (
    CompositeValidator,
    ConfigValidator,
    InputSanitizer,
    ValidationLevel,
    create_command_validator,
    create_file_validator,
    validate_args,
)

logger = logging.getLogger(__name__)


@dataclass
class IntegratedAgentConfig:
    """Configuration for the integrated agent system."""

    # Core settings
    model: str
    system_prompt: str
    workspace: Path

    # Performance settings
    enable_caching: bool = True
    cache_strategy: CacheStrategy = CacheStrategy.LRU
    cache_size: int = 1000
    disk_cache_dir: Optional[Path] = None

    # Validation settings
    validation_level: ValidationLevel = ValidationLevel.STANDARD
    sanitize_inputs: bool = True

    # Execution settings
    max_parallel_tools: int = 5
    tool_timeout: float = 120.0
    enable_rate_limiting: bool = True
    max_api_calls_per_second: int = 10

    # Monitoring settings
    enable_monitoring: bool = True
    log_level: str = "INFO"
    profile_performance: bool = False

    # Safety settings
    allow_dangerous_commands: bool = False
    require_confirmation: bool = True
    max_file_size_mb: int = 100

    def validate(self) -> bool:
        """Validate configuration."""
        validator = ConfigValidator({
            "model": str,
            "system_prompt": str,
            "workspace": Path,
        })

        result = validator.validate({
            "model": self.model,
            "system_prompt": self.system_prompt,
            "workspace": self.workspace,
        })

        if not result.valid:
            raise ValueError(f"Invalid configuration: {result.errors}")

        return True


class IntegratedToolSystem:
    """Integrated tool system with all enhancements."""

    def __init__(self, config: IntegratedAgentConfig):
        self.config = config
        self.console = Console()

        # Initialize components
        self._init_caching()
        self._init_validation()
        self._init_monitoring()
        self._init_tools()

    def _init_caching(self) -> None:
        """Initialize caching systems."""
        if self.config.enable_caching:
            # Memory cache
            self.memory_cache = AdvancedCache(
                max_size=self.config.cache_size,
                strategy=self.config.cache_strategy
            )

            # Disk cache for large objects
            if self.config.disk_cache_dir:
                self.disk_cache = DiskCache(
                    cache_dir=self.config.disk_cache_dir,
                    max_size_mb=self.config.max_file_size_mb * 10
                )
            else:
                self.disk_cache = None
        else:
            self.memory_cache = None
            self.disk_cache = None

    def _init_validation(self) -> None:
        """Initialize validation systems."""
        self.file_validator = create_file_validator()
        self.command_validator = create_command_validator()
        self.sanitizer = InputSanitizer()

    def _init_monitoring(self) -> None:
        """Initialize monitoring systems."""
        if self.config.enable_monitoring:
            self.tool_monitor = ToolMonitor()
            self.performance_monitor = {}

            # Set up logging
            logging.basicConfig(
                level=getattr(logging, self.config.log_level),
                format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
        else:
            self.tool_monitor = None

    def _init_tools(self) -> None:
        """Initialize tool registry with enhanced tools."""
        self.tool_registry = ToolRegistry()

        # Register enhanced file tools
        self._register_file_tools()

        # Register enhanced execution tools
        self._register_execution_tools()

        # Register network tools
        self._register_network_tools()

        # Initialize parallel executor
        self.parallel_executor = ParallelToolExecutor(self.tool_registry)

        # Initialize rate limiter
        if self.config.enable_rate_limiting:
            self.rate_limiter = RateLimiter(
                max_calls=self.config.max_api_calls_per_second,
                time_window=1.0
            )
        else:
            self.rate_limiter = None

    def _register_file_tools(self) -> None:
        """Register enhanced file system tools."""

        # Enhanced read file with caching
        @memoize(maxsize=100, ttl=300)
        async def read_file_cached(path: str, **kwargs) -> str:
            """Read file with caching."""
            # Validate path
            if self.config.sanitize_inputs:
                path = self.sanitizer.sanitize_path(path)

            validation = self.file_validator.validate(
                path,
                level=self.config.validation_level
            )
            if not validation.valid:
                raise ValueError(f"Invalid path: {validation.errors}")

            # Read file
            target = self.config.workspace / path
            if not target.exists():
                raise FileNotFoundError(f"File not found: {path}")

            return target.read_text(encoding=kwargs.get("encoding", "utf-8"))

        read_tool = create_enhanced_tool(
            name="read_file",
            category="file_system",
            description="Read file with validation and caching",
            func=read_file_cached,
            cacheable=True,
            timeout=30.0
        )
        self.tool_registry.register(read_tool)

        # Enhanced write file with validation
        async def write_file_validated(path: str, content: str, **kwargs) -> str:
            """Write file with validation."""
            # Validate and sanitize
            if self.config.sanitize_inputs:
                path = self.sanitizer.sanitize_path(path)

            validation = self.file_validator.validate(
                path,
                level=self.config.validation_level
            )
            if not validation.valid:
                raise ValueError(f"Invalid path: {validation.errors}")

            # Check file size
            size_mb = len(content.encode()) / (1024 * 1024)
            if size_mb > self.config.max_file_size_mb:
                raise ValueError(f"File too large: {size_mb:.2f} MB")

            # Write file
            target = self.config.workspace / path
            target.parent.mkdir(parents=True, exist_ok=True)

            # Atomic write
            import tempfile
            with tempfile.NamedTemporaryFile(
                mode="w",
                dir=target.parent,
                delete=False
            ) as tmp:
                tmp.write(content)
                tmp_path = Path(tmp.name)

            tmp_path.replace(target)
            return f"Wrote {len(content)} bytes to {path}"

        write_tool = create_enhanced_tool(
            name="write_file",
            category="file_system",
            description="Write file with validation and atomic operations",
            func=write_file_validated,
            requires_confirmation=self.config.require_confirmation,
            timeout=30.0
        )
        self.tool_registry.register(write_tool)

    def _register_execution_tools(self) -> None:
        """Register enhanced code execution tools."""

        async def run_shell_safe(command: str, **kwargs) -> str:
            """Run shell command with safety checks."""
            # Validate command
            if self.config.sanitize_inputs:
                # Check for dangerous patterns
                if not self.config.allow_dangerous_commands:
                    dangerous = ["rm -rf", "dd if=", ":(){ :|:& };:"]
                    for pattern in dangerous:
                        if pattern in command:
                            raise ValueError(f"Dangerous command pattern: {pattern}")

            validation = self.command_validator.validate(
                command,
                level=self.config.validation_level
            )
            if not validation.valid:
                raise ValueError(f"Invalid command: {validation.errors}")

            # Execute with timeout
            import subprocess
            try:
                result = subprocess.run(
                    command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=kwargs.get("timeout", self.config.tool_timeout),
                    cwd=str(self.config.workspace)
                )

                output = result.stdout
                if result.stderr:
                    output += f"\n[stderr]\n{result.stderr}"

                if result.returncode != 0:
                    output += f"\n[exit code: {result.returncode}]"

                return output

            except subprocess.TimeoutExpired:
                return f"Command timed out after {kwargs.get('timeout', self.config.tool_timeout)} seconds"

        shell_tool = create_enhanced_tool(
            name="run_shell",
            category="execution",
            description="Execute shell commands with safety validation",
            func=run_shell_safe,
            requires_confirmation=self.config.require_confirmation,
            parallel_safe=False,
            timeout=self.config.tool_timeout
        )
        self.tool_registry.register(shell_tool)

    def _register_network_tools(self) -> None:
        """Register network tools with rate limiting."""

        async def web_search_limited(query: str, **kwargs) -> str:
            """Web search with rate limiting."""
            if self.rate_limiter:
                await self.rate_limiter.acquire()

            # Check cache first
            if self.memory_cache:
                cache_key = f"search_{query}"
                cached = await self.memory_cache.get(cache_key)
                if cached:
                    return cached

            # Simulate search (replace with actual implementation)
            results = f"Search results for: {query}\n"
            results += "1. Result 1\n2. Result 2\n3. Result 3"

            # Cache results
            if self.memory_cache:
                await self.memory_cache.set(cache_key, results, ttl=300)

            return results

        search_tool = create_enhanced_tool(
            name="web_search",
            category="network",
            description="Web search with caching and rate limiting",
            func=web_search_limited,
            cacheable=True,
            timeout=30.0
        )
        self.tool_registry.register(search_tool)

    async def execute_tool(
        self,
        tool_name: str,
        params: Dict[str, Any]
    ) -> ToolResult:
        """Execute a tool with all enhancements."""
        tool = self.tool_registry.get(tool_name)
        if not tool:
            raise ValueError(f"Tool not found: {tool_name}")

        # Profile if enabled
        if self.config.profile_performance:
            start_time = time.perf_counter()

        # Execute tool
        result = await tool(**params)

        # Monitor execution
        if self.tool_monitor:
            self.tool_monitor.record_execution(tool_name, result, params)

        # Profile if enabled
        if self.config.profile_performance:
            elapsed = time.perf_counter() - start_time
            logger.info(f"Tool {tool_name} executed in {elapsed:.3f}s")

        return result

    async def execute_parallel(
        self,
        tasks: List[Dict[str, Any]]
    ) -> List[ToolResult]:
        """Execute multiple tools in parallel."""
        return await self.parallel_executor.execute_parallel(
            tasks,
            max_concurrent=self.config.max_parallel_tools
        )

    def get_statistics(self) -> Dict[str, Any]:
        """Get system statistics."""
        stats = {
            "tools_registered": len(self.tool_registry.list_all()),
        }

        if self.tool_monitor:
            stats["tool_stats"] = self.tool_monitor.get_statistics()

        if self.memory_cache:
            stats["cache_stats"] = self.memory_cache.get_stats()

        return stats


class IntegratedAgent:
    """Main integrated agent with all enhancements."""

    def __init__(self, options: AgentOptions):
        self.options = options
        self.console = Console()

        # Create integrated configuration
        self.config = IntegratedAgentConfig(
            model=options.model,
            system_prompt=options.system_prompt,
            workspace=options.workspace,
            enable_caching=True,
            validation_level=ValidationLevel.STANDARD,
            enable_monitoring=True,
            allow_dangerous_commands=options.execution_mode == ExecutionMode.UNRESTRICTED,
            require_confirmation=not options.auto_approve,
        )

        # Validate configuration
        self.config.validate()

        # Initialize integrated tool system
        self.tool_system = IntegratedToolSystem(self.config)

        # Initialize execution context
        self.context = ExecutionContext(
            workspace=options.workspace,
            model=options.model,
            system_prompt=options.system_prompt,
            user_prompt=options.user_prompt,
            max_steps=options.max_steps,
            allow_global_access=options.allow_global_access,
            execution_mode=options.execution_mode,
            auto_approve=options.auto_approve,
            stream_output=options.stream_output,
            enable_reasoning=options.enable_reasoning,
        )

        # Set tool registry in context
        self.context.tool_registry = self.tool_system.tool_registry
        self.context.tool_monitor = self.tool_system.tool_monitor

    async def run(self) -> Dict[str, Any]:
        """Run the integrated agent."""
        logger.info("Starting integrated agent execution")

        # Create orchestrator with enhanced context
        orchestrator = EnhancedAgentOrchestrator(self.context)

        # Display initial status
        self._display_status("Initializing agent...")

        try:
            # Run the agent
            result = await orchestrator.run()

            # Display statistics
            self._display_statistics()

            return result

        except Exception as e:
            logger.error(f"Agent execution failed: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "statistics": self.tool_system.get_statistics()
            }

    def _display_status(self, message: str) -> None:
        """Display status message."""
        panel = Panel(
            message,
            title="Agent Status",
            border_style="cyan"
        )
        self.console.print(panel)

    def _display_statistics(self) -> None:
        """Display execution statistics."""
        stats = self.tool_system.get_statistics()

        table = Table(title="Execution Statistics", show_header=True)
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")

        # Add statistics rows
        table.add_row("Tools Registered", str(stats.get("tools_registered", 0)))

        if "tool_stats" in stats:
            tool_stats = stats["tool_stats"]
            table.add_row("Total Executions", str(tool_stats.get("total_executions", 0)))
            table.add_row("Success Rate", f"{tool_stats.get('success_rate', 0):.1%}")
            table.add_row("Average Time", f"{tool_stats.get('average_execution_time', 0):.2f}s")

        if "cache_stats" in stats:
            cache_stats = stats["cache_stats"]
            table.add_row("Cache Hit Rate", f"{cache_stats.get('hit_rate', 0):.1%}")
            table.add_row("Cache Size", str(cache_stats.get("size", 0)))

        self.console.print(table)


def run_integrated_agent(options: AgentOptions) -> None:
    """Run the integrated agent with all enhancements."""
    agent = IntegratedAgent(options)

    # Run asynchronously
    result = asyncio.run(agent.run())

    # Display final result
    console = Console()
    if result.get("success"):
        console.print(
            Panel(
                result.get("summary", "Execution completed successfully"),
                title="✅ Success",
                border_style="green"
            )
        )
    else:
        console.print(
            Panel(
                result.get("error", "Execution failed"),
                title="❌ Error",
                border_style="red"
            )
        )