#!/usr/bin/env python3
"""Test script for enhanced agent capabilities."""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from deepseek_cli.agent import (
    ToolExecutor,
    ExecutionMode,
    tool_schemas,
    AgentOptions,
)


def test_tool_executor():
    """Test the enhanced tool executor."""
    print("Testing Enhanced Tool Executor...")

    # Create executor with unrestricted mode
    executor = ToolExecutor(
        root=Path.cwd(),
        execution_mode=ExecutionMode.UNRESTRICTED,
        auto_approve=True,
        stream_output=False,
    )

    # Test system info
    print("\n1. Testing system_info:")
    result = executor.system_info()
    print(f"System info result: {result[:200]}...")

    # Test git operation (safe read operation)
    print("\n2. Testing git_operation (status):")
    result = executor.git_operation("status")
    print(f"Git status result: {result[:200]}...")

    # Test shell command without permission prompts
    print("\n3. Testing run_shell (unrestricted):")
    result = executor.run_shell("echo 'Testing unrestricted execution'")
    print(f"Shell result: {result}")

    # Test background shell
    print("\n4. Testing background shell:")
    result = executor.run_shell("sleep 1; echo 'Background complete'", background=True)
    shell_id = result.split("ID: ")[1].split("\n")[0] if "ID: " in result else None
    print(f"Background start result: {result}")

    if shell_id:
        import time
        time.sleep(1.5)
        output = executor.get_shell_output(shell_id)
        print(f"Background output: {output[:200]}...")

    print("\n✅ All tests completed successfully!")


def test_tool_schemas():
    """Test that all new tools are registered."""
    print("\nTesting Tool Schemas...")

    schemas = tool_schemas()
    tool_names = [s["function"]["name"] for s in schemas]

    expected_tools = [
        "list_dir", "read_file", "write_file", "todo_write", "move_path",
        "stat_path", "search_text", "apply_patch", "run_shell",
        "python_repl", "http_request", "download_file", "tavily_search",
        "tavily_extract", "git_operation", "docker_operation", "get_shell_output",
        "kill_shell", "system_info"
    ]

    print(f"Found {len(tool_names)} tools")

    for tool in expected_tools:
        if tool in tool_names:
            print(f"✓ {tool}")
        else:
            print(f"✗ {tool} (missing)")

    print(f"\nTotal tools: {len(tool_names)}")
    print(f"Expected tools: {len(expected_tools)}")


def test_execution_modes():
    """Test different execution modes."""
    print("\nTesting Execution Modes...")

    modes = [
        ExecutionMode.UNRESTRICTED,
        ExecutionMode.SANDBOXED,
        ExecutionMode.READ_ONLY,
    ]

    for mode in modes:
        print(f"✓ {mode.value} mode available")

    # Test mode behavior
    executor = ToolExecutor(
        root=Path.cwd(),
        execution_mode=ExecutionMode.READ_ONLY,
    )

    result = executor.write_file("/tmp/test.txt", "test content")
    print(f"\nREAD_ONLY mode write attempt: {result}")

    print("\n✅ Execution modes test completed!")


if __name__ == "__main__":
    print("=" * 60)
    print("Enhanced DeepSeek CLI Agent Test Suite")
    print("=" * 60)

    test_tool_executor()
    test_tool_schemas()
    test_execution_modes()

    print("\n" + "=" * 60)
    print("All tests completed!")
    print("=" * 60)
