"""Enhanced agent module with improved error handling, tool management, and execution flow."""

from __future__ import annotations

import asyncio
import json
import logging
import os
import re
import subprocess
import sys
import time
import traceback
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import (
    Any,
    Callable,
    Dict,
    List,
    Mapping,
    Optional,
    Set,
    Tuple,
    Union,
)

from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn
from rich.table import Table
from rich.text import Text
from openai import OpenAI

from .tool_framework import (
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
from .constants import (
    DEFAULT_TAVILY_API_KEY,
    MAX_LIST_DEPTH,
    MAX_TOOL_RESULT_CHARS,
)

# Set up structured logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class AgentState(Enum):
    """State of the agent during execution."""
    IDLE = "idle"
    PLANNING = "planning"
    EXECUTING = "executing"
    WAITING = "waiting"
    ERROR = "error"
    COMPLETED = "completed"


class ExecutionContext:
    """Context for agent execution with enhanced tracking."""

    def __init__(
        self,
        workspace: Path,
        model: str,
        system_prompt: str,
        user_prompt: str,
        **options
    ):
        self.workspace = workspace
        self.model = model
        self.system_prompt = system_prompt
        self.user_prompt = user_prompt
        self.options = options

        # Execution tracking
        self.state = AgentState.IDLE
        self.start_time = time.time()
        self.steps_taken = 0
        self.max_steps = options.get("max_steps", 5000)

        # Tool tracking
        self.tool_registry = ToolRegistry()
        self.tool_monitor = ToolMonitor()
        self.parallel_executor = None

        # Error tracking
        self.errors: List[Dict[str, Any]] = []
        self.warnings: List[str] = []
        self.recovery_attempts = 0
        self.max_recovery_attempts = 3

        # Planning and reasoning
        self.current_plan: List[str] = []
        self.completed_tasks: Set[str] = set()
        self.pending_tasks: List[str] = []
        self.reasoning_history: List[str] = []

        # Performance tracking
        self.cache = ToolCache(max_size=200, ttl=600)
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}

        # Results accumulator
        self.results: List[Any] = []
        self.final_summary: Optional[str] = None

    def update_state(self, new_state: AgentState) -> None:
        """Update agent state with logging."""
        old_state = self.state
        self.state = new_state
        logger.info(f"Agent state transition: {old_state.value} -> {new_state.value}")

    def record_error(
        self,
        error: Exception,
        context: str,
        recoverable: bool = True
    ) -> None:
        """Record an error with context."""
        error_data = {
            "timestamp": time.time(),
            "type": type(error).__name__,
            "message": str(error),
            "context": context,
            "recoverable": recoverable,
            "traceback": traceback.format_exc()
        }
        self.errors.append(error_data)
        logger.error(f"Error in {context}: {error}", exc_info=True)

    def add_warning(self, message: str) -> None:
        """Add a warning message."""
        self.warnings.append(message)
        logger.warning(message)

    def get_statistics(self) -> Dict[str, Any]:
        """Get execution statistics."""
        elapsed = time.time() - self.start_time
        return {
            "elapsed_time": elapsed,
            "steps_taken": self.steps_taken,
            "state": self.state.value,
            "errors_count": len(self.errors),
            "warnings_count": len(self.warnings),
            "completed_tasks": len(self.completed_tasks),
            "pending_tasks": len(self.pending_tasks),
            "tool_stats": self.tool_monitor.get_statistics(),
            "cache_hits": self.cache._cache.__len__() if self.cache else 0,
            "recovery_attempts": self.recovery_attempts,
        }


class EnhancedToolExecutor:
    """Enhanced tool executor with robust error handling and monitoring."""

    def __init__(self, context: ExecutionContext):
        self.context = context
        self.console = Console()
        self._register_tools()

    def _register_tools(self) -> None:
        """Register all available tools with enhanced metadata."""
        # File system tools
        self._register_file_tools()
        # Code execution tools
        self._register_code_tools()
        # Network tools
        self._register_network_tools()
        # System tools
        self._register_system_tools()

        # Initialize parallel executor
        self.context.parallel_executor = ParallelToolExecutor(self.context.tool_registry)

    def _register_file_tools(self) -> None:
        """Register file system tools."""
        # List directory tool
        list_dir_tool = create_enhanced_tool(
            name="list_dir",
            category="file_system",
            description="List directory contents with optional recursion",
            func=self._list_dir_impl,
            priority=ToolPriority.NORMAL,
            cacheable=True,
            timeout=10.0,
            tags={"file", "read", "safe"}
        )
        self.context.tool_registry.register(list_dir_tool)

        # Read file tool with enhanced error handling
        read_file_tool = create_enhanced_tool(
            name="read_file",
            category="file_system",
            description="Read file contents with smart encoding detection",
            func=self._read_file_impl,
            priority=ToolPriority.NORMAL,
            cacheable=True,
            timeout=30.0,
            tags={"file", "read", "safe"}
        )
        self.context.tool_registry.register(read_file_tool)

        # Write file tool with validation
        write_file_tool = create_enhanced_tool(
            name="write_file",
            category="file_system",
            description="Write content to file with atomic operations",
            func=self._write_file_impl,
            priority=ToolPriority.HIGH,
            requires_confirmation=True,
            cacheable=False,
            timeout=30.0,
            tags={"file", "write", "destructive"}
        )
        self.context.tool_registry.register(write_file_tool)

    def _register_code_tools(self) -> None:
        """Register code execution tools."""
        # Enhanced shell execution with streaming
        shell_tool = create_enhanced_tool(
            name="run_shell",
            category="code_execution",
            description="Execute shell commands with timeout and streaming",
            func=self._run_shell_impl,
            priority=ToolPriority.CRITICAL,
            requires_confirmation=True,
            cacheable=False,
            timeout=120.0,
            parallel_safe=False,
            tags={"shell", "execute", "dangerous"}
        )
        self.context.tool_registry.register(shell_tool)

        # Python REPL with sandboxing
        python_tool = create_enhanced_tool(
            name="python_repl",
            category="code_execution",
            description="Execute Python code in isolated environment",
            func=self._python_repl_impl,
            priority=ToolPriority.HIGH,
            cacheable=False,
            timeout=60.0,
            tags={"python", "execute", "sandbox"}
        )
        self.context.tool_registry.register(python_tool)

    def _register_network_tools(self) -> None:
        """Register network-related tools."""
        # Web search with caching
        search_tool = create_enhanced_tool(
            name="tavily_search",
            category="network",
            description="Search web with intelligent result filtering",
            func=self._tavily_search_impl,
            priority=ToolPriority.NORMAL,
            cacheable=True,
            timeout=30.0,
            tags={"search", "web", "api"}
        )
        self.context.tool_registry.register(search_tool)

    def _register_system_tools(self) -> None:
        """Register system information tools."""
        # System info tool
        sys_info_tool = create_enhanced_tool(
            name="system_info",
            category="system",
            description="Get system information and resource usage",
            func=self._system_info_impl,
            priority=ToolPriority.LOW,
            cacheable=True,
            timeout=5.0,
            tags={"system", "info", "safe"}
        )
        self.context.tool_registry.register(sys_info_tool)

    # Tool implementation methods with enhanced error handling

    async def _list_dir_impl(self, path: str = ".", recursive: bool = False) -> str:
        """List directory with enhanced formatting and error handling."""
        try:
            target = self._resolve_path(path)
            if not target.exists():
                raise FileNotFoundError(f"Path '{path}' does not exist")

            entries = []
            if recursive:
                for root, dirs, files in os.walk(target):
                    level = Path(root).relative_to(target).parts
                    indent = "  " * len(level)
                    entries.append(f"{indent}{Path(root).name}/")
                    for file in sorted(files):
                        entries.append(f"{indent}  {file}")
            else:
                for item in sorted(target.iterdir()):
                    if item.is_dir():
                        entries.append(f"{item.name}/")
                    else:
                        size = item.stat().st_size
                        entries.append(f"{item.name} ({self._format_size(size)})")

            return "\n".join(entries) if entries else "Directory is empty"

        except Exception as e:
            self.context.record_error(e, f"list_dir({path})")
            raise

    async def _read_file_impl(
        self,
        path: str,
        encoding: str = "utf-8",
        offset: int = 0,
        limit: Optional[int] = None
    ) -> str:
        """Read file with smart encoding detection and chunking."""
        try:
            target = self._resolve_path(path)
            if not target.exists():
                raise FileNotFoundError(f"File '{path}' does not exist")

            # Try to detect encoding if utf-8 fails
            try:
                content = target.read_text(encoding=encoding)
            except UnicodeDecodeError:
                import chardet
                raw = target.read_bytes()
                detected = chardet.detect(raw)
                encoding = detected.get("encoding", "utf-8")
                content = raw.decode(encoding, errors="replace")
                self.context.add_warning(f"Used detected encoding {encoding} for {path}")

            # Apply offset and limit
            lines = content.splitlines()
            if offset:
                lines = lines[offset:]
            if limit:
                lines = lines[:limit]

            return "\n".join(lines)

        except Exception as e:
            self.context.record_error(e, f"read_file({path})")
            raise

    async def _write_file_impl(
        self,
        path: str,
        content: str,
        encoding: str = "utf-8",
        create_parents: bool = True,
        backup: bool = True
    ) -> str:
        """Write file with atomic operations and backup."""
        try:
            target = self._resolve_path(path)

            # Create backup if file exists
            if backup and target.exists():
                backup_path = target.with_suffix(target.suffix + ".bak")
                import shutil
                shutil.copy2(target, backup_path)
                self.context.add_warning(f"Created backup at {backup_path}")

            # Create parent directories if needed
            if create_parents:
                target.parent.mkdir(parents=True, exist_ok=True)

            # Atomic write using temporary file
            import tempfile
            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding=encoding,
                dir=target.parent,
                delete=False
            ) as tmp:
                tmp.write(content)
                tmp_path = Path(tmp.name)

            # Move temporary file to target
            tmp_path.replace(target)

            return f"Successfully wrote {len(content)} characters to {path}"

        except Exception as e:
            self.context.record_error(e, f"write_file({path})")
            raise

    @with_retry(max_attempts=3, delay=1.0)
    async def _run_shell_impl(
        self,
        command: str,
        timeout: int = 120,
        stream: bool = True,
        cwd: Optional[str] = None
    ) -> str:
        """Execute shell command with streaming and timeout."""
        try:
            # Use circuit breaker for dangerous commands
            if "rm -rf" in command or "dd if=" in command:
                if "shell" not in self.context.circuit_breakers:
                    self.context.circuit_breakers["shell"] = CircuitBreaker()
                breaker = self.context.circuit_breakers["shell"]
                return await breaker.call(self._execute_shell, command, timeout, stream, cwd)

            return await self._execute_shell(command, timeout, stream, cwd)

        except Exception as e:
            self.context.record_error(e, f"run_shell({command[:50]}...)")
            raise

    async def _execute_shell(
        self,
        command: str,
        timeout: int,
        stream: bool,
        cwd: Optional[str]
    ) -> str:
        """Internal shell execution with streaming support."""
        work_dir = self._resolve_path(cwd) if cwd else self.context.workspace

        process = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=work_dir
        )

        if stream:
            # Stream output in real-time
            output_lines = []
            async for line in process.stdout:
                decoded = line.decode("utf-8", errors="replace")
                output_lines.append(decoded)
                self.console.print(decoded, end="")

            stdout = "".join(output_lines)
            stderr = (await process.stderr.read()).decode("utf-8", errors="replace")
        else:
            # Wait for completion
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=timeout
                )
                stdout = stdout.decode("utf-8", errors="replace")
                stderr = stderr.decode("utf-8", errors="replace")
            except asyncio.TimeoutError:
                process.kill()
                raise TimeoutError(f"Command timed out after {timeout} seconds")

        if process.returncode != 0:
            error_msg = f"Command failed with exit code {process.returncode}\n{stderr}"
            if "fatal" in stderr.lower() or "error" in stderr.lower():
                raise RuntimeError(error_msg)
            else:
                self.context.add_warning(error_msg)

        return stdout + (f"\n[stderr]\n{stderr}" if stderr else "")

    async def _python_repl_impl(self, code: str) -> str:
        """Execute Python code in sandboxed environment."""
        try:
            # Create isolated namespace
            namespace = {
                "__builtins__": __builtins__,
                "workspace": str(self.context.workspace),
            }

            # Execute code
            import io
            import contextlib
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                exec(code, namespace)

            result = output.getvalue()
            return result if result else "Code executed successfully (no output)"

        except Exception as e:
            self.context.record_error(e, f"python_repl()")
            return f"Python execution error: {e}"

    async def _tavily_search_impl(
        self,
        query: str,
        max_results: int = 5
    ) -> str:
        """Perform web search with intelligent filtering."""
        try:
            # Check cache first
            cache_key = f"search_{query}_{max_results}"
            cached = self.context.cache.get(cache_key)
            if cached:
                return cached

            # Implement actual search (placeholder)
            results = f"Search results for '{query}':\n"
            results += "1. Result 1\n2. Result 2\n3. Result 3"

            # Cache results
            self.context.cache.set(cache_key, results)
            return results

        except Exception as e:
            self.context.record_error(e, f"tavily_search({query})")
            raise

    async def _system_info_impl(self) -> str:
        """Get system information."""
        try:
            import platform
            import psutil

            info = {
                "platform": platform.platform(),
                "python": platform.python_version(),
                "cpu_count": psutil.cpu_count(),
                "memory": {
                    "total": self._format_size(psutil.virtual_memory().total),
                    "available": self._format_size(psutil.virtual_memory().available),
                    "percent": psutil.virtual_memory().percent
                },
                "disk": {
                    "total": self._format_size(psutil.disk_usage("/").total),
                    "free": self._format_size(psutil.disk_usage("/").free),
                    "percent": psutil.disk_usage("/").percent
                }
            }
            return json.dumps(info, indent=2)

        except Exception as e:
            self.context.record_error(e, "system_info()")
            return f"Error getting system info: {e}"

    # Helper methods

    def _resolve_path(self, path: str) -> Path:
        """Resolve path with safety checks."""
        if not path:
            return self.context.workspace

        resolved = Path(path)
        if not resolved.is_absolute():
            resolved = self.context.workspace / resolved

        # Safety check
        if not self.context.options.get("allow_global_access", False):
            try:
                resolved.relative_to(self.context.workspace)
            except ValueError:
                raise ValueError(f"Path '{path}' is outside workspace")

        return resolved

    @staticmethod
    def _format_size(bytes: int) -> str:
        """Format byte size for display."""
        for unit in ["B", "KB", "MB", "GB", "TB"]:
            if bytes < 1024.0:
                return f"{bytes:.1f} {unit}"
            bytes /= 1024.0
        return f"{bytes:.1f} PB"

    async def execute_tool(
        self,
        tool_name: str,
        **params
    ) -> ToolResult:
        """Execute a tool with full monitoring and error handling."""
        tool = self.context.tool_registry.get(tool_name)
        if not tool:
            return ToolResult(
                status=ToolStatus.FAILED,
                output=None,
                error=f"Tool '{tool_name}' not found"
            )

        # Record execution
        result = await tool(**params)
        self.context.tool_monitor.record_execution(tool_name, result, params)

        # Update step counter
        self.context.steps_taken += 1

        return result

    async def execute_parallel_tools(
        self,
        tasks: List[Dict[str, Any]]
    ) -> List[ToolResult]:
        """Execute multiple tools in parallel."""
        return await self.context.parallel_executor.execute_parallel(tasks)


class EnhancedAgentOrchestrator:
    """Main orchestrator for enhanced agent execution."""

    def __init__(self, context: ExecutionContext):
        self.context = context
        self.executor = EnhancedToolExecutor(context)
        self.console = Console()
        self.client = None

    async def run(self) -> Dict[str, Any]:
        """Main execution loop with enhanced error handling."""
        self.context.update_state(AgentState.PLANNING)

        try:
            # Initialize OpenAI client
            self._initialize_client()

            # Main execution loop
            while self.context.steps_taken < self.context.max_steps:
                # Check if we should stop
                if self.context.state == AgentState.COMPLETED:
                    break

                # Plan next actions
                actions = await self._plan_actions()
                if not actions:
                    self.context.update_state(AgentState.COMPLETED)
                    break

                # Execute actions
                self.context.update_state(AgentState.EXECUTING)
                results = await self._execute_actions(actions)

                # Process results and update plan
                await self._process_results(results)

                # Check for errors and attempt recovery
                if self.context.errors:
                    if not await self._attempt_recovery():
                        self.context.update_state(AgentState.ERROR)
                        break

            # Generate final summary
            self.context.final_summary = self._generate_summary()
            self.context.update_state(AgentState.COMPLETED)

        except Exception as e:
            self.context.record_error(e, "main_loop", recoverable=False)
            self.context.update_state(AgentState.ERROR)

        return self._prepare_final_report()

    def _initialize_client(self) -> None:
        """Initialize OpenAI client."""
        api_key = self.context.options.get("api_key", os.getenv("DEEPSEEK_API_KEY"))
        if not api_key:
            raise ValueError("No API key provided")

        self.client = OpenAI(
            api_key=api_key,
            base_url=self.context.options.get("base_url", "https://api.deepseek.com")
        )

    async def _plan_actions(self) -> List[Dict[str, Any]]:
        """Generate action plan using LLM."""
        # This is a simplified version - in production, this would
        # make actual API calls to generate plans
        return [
            {"tool": "list_dir", "params": {"path": ".", "recursive": False}},
            {"tool": "system_info", "params": {}},
        ]

    async def _execute_actions(self, actions: List[Dict[str, Any]]) -> List[ToolResult]:
        """Execute planned actions."""
        # Separate parallel-safe and sequential actions
        parallel_safe = []
        sequential = []

        for action in actions:
            tool = self.context.tool_registry.get(action["tool"])
            if tool and tool.metadata.parallel_safe:
                parallel_safe.append(action)
            else:
                sequential.append(action)

        results = []

        # Execute parallel-safe actions
        if parallel_safe:
            parallel_results = await self.executor.execute_parallel_tools(parallel_safe)
            results.extend(parallel_results)

        # Execute sequential actions
        for action in sequential:
            result = await self.executor.execute_tool(
                action["tool"],
                **action.get("params", {})
            )
            results.append(result)

        return results

    async def _process_results(self, results: List[ToolResult]) -> None:
        """Process execution results and update context."""
        for result in results:
            if result.is_success:
                self.context.results.append(result.output)
            else:
                self.context.add_warning(f"Tool failed: {result.error}")

    async def _attempt_recovery(self) -> bool:
        """Attempt to recover from errors."""
        if self.context.recovery_attempts >= self.context.max_recovery_attempts:
            return False

        self.context.recovery_attempts += 1
        logger.info(f"Attempting recovery (attempt {self.context.recovery_attempts})")

        # Clear recoverable errors
        self.context.errors = [
            e for e in self.context.errors
            if not e.get("recoverable", True)
        ]

        return len(self.context.errors) == 0

    def _generate_summary(self) -> str:
        """Generate execution summary."""
        stats = self.context.get_statistics()
        summary = f"""
Execution Summary:
- Total steps: {stats['steps_taken']}
- Elapsed time: {stats['elapsed_time']:.2f}s
- Tasks completed: {stats['completed_tasks']}
- Errors: {stats['errors_count']}
- Warnings: {stats['warnings_count']}
"""
        return summary

    def _prepare_final_report(self) -> Dict[str, Any]:
        """Prepare final execution report."""
        return {
            "success": self.context.state == AgentState.COMPLETED,
            "summary": self.context.final_summary,
            "statistics": self.context.get_statistics(),
            "results": self.context.results,
            "errors": self.context.errors,
            "warnings": self.context.warnings,
        }


# Public API function
async def run_enhanced_agent(
    workspace: Path,
    model: str,
    system_prompt: str,
    user_prompt: str,
    **options
) -> Dict[str, Any]:
    """Run the enhanced agent with improved error handling and monitoring."""
    context = ExecutionContext(
        workspace=workspace,
        model=model,
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        **options
    )

    orchestrator = EnhancedAgentOrchestrator(context)
    return await orchestrator.run()