"""Agent execution primitives for the DeepSeek CLI with enhanced capabilities."""

from __future__ import annotations

import asyncio
import json
import os
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple

from contextlib import nullcontext
from rich.console import Console
from rich.live import Live
from rich.text import Text
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from openai import OpenAI

from .constants import DEFAULT_TAVILY_API_KEY, MAX_LIST_DEPTH, MAX_TOOL_RESULT_CHARS

ToolResult = str


class ExecutionMode(Enum):
    """Execution mode for operations."""
    UNRESTRICTED = "unrestricted"  # No permission checks, direct execution
    SANDBOXED = "sandboxed"  # Limited to workspace
    READ_ONLY = "read_only"  # No write operations


class ToolCategory(Enum):
    """Categories of tools for organization and display."""
    FILE_SYSTEM = "file_system"
    CODE_EXECUTION = "code_execution"
    NETWORK = "network"
    SYSTEM = "system"
    SEARCH = "search"


_PLAN_SECTION_HEADERS = (
    "plan:",
    "action plan:",
    "execution plan:",
    "approach:",
    "strategy:",
    "steps:",
    "next steps:",
)
_PLAN_NUMERIC_RE = re.compile(r"^\d+[\.\)]\s+")
_PLAN_BULLET_RE = re.compile(r"^[\-\*\u2022]\s+(.*)")


def _extract_text_chunks(payload: object) -> Iterable[str]:
    """Normalize chat content variants (strings, dicts, typed objects) into text."""
    if payload is None:
        return []
    if isinstance(payload, str):
        return [payload]
    chunks: List[str] = []
    if isinstance(payload, Sequence) and not isinstance(payload, (str, bytes, bytearray)):
        for item in payload:
            chunks.extend(_extract_text_chunks(item))
        return chunks
    if isinstance(payload, dict):
        text = payload.get("text")
        if text:
            chunks.append(str(text))
        return chunks
    text_attr = getattr(payload, "text", None)
    if text_attr:
        chunks.append(str(text_attr))
    return chunks


def _extract_plan_lines(text: str) -> List[str]:
    """Best-effort detection of plan bullets within assistant reasoning."""
    if not text:
        return []
    plan_lines: List[str] = []
    collecting = False
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            if collecting and plan_lines:
                break
            continue
        lower = line.lower()
        if any(lower.startswith(header) for header in _PLAN_SECTION_HEADERS):
            collecting = True
            remainder = line.split(":", 1)[1].strip() if ":" in line else ""
            if remainder:
                plan_lines.append(remainder)
            continue
        numeric_match = _PLAN_NUMERIC_RE.match(line)
        bullet_match = _PLAN_BULLET_RE.match(line)
        if numeric_match:
            collecting = True
            plan_lines.append(line)
            continue
        if bullet_match:
            collecting = True
            plan_lines.append(bullet_match.group(1).strip() or line)
            continue
        if collecting and plan_lines:
            # Treat indented follow-up sentences as part of the previous bullet.
            plan_lines[-1] = plan_lines[-1] + f" {line}"
    normalized: List[str] = []
    for idx, entry in enumerate(plan_lines, start=1):
        if _PLAN_NUMERIC_RE.match(entry):
            normalized.append(entry)
        else:
            normalized.append(f"{idx}. {entry}")
    # Reduce noise and prevent flooding the terminal.
    return normalized[:6]


def _default_file_mode() -> int:
    current_umask = os.umask(0)
    os.umask(current_umask)
    return 0o666 & ~current_umask


@dataclass
class AgentOptions:
    """Options controlling the agent orchestration loop with enhanced capabilities."""

    model: str
    system_prompt: str
    user_prompt: str
    follow_up: List[str]
    workspace: Path
    read_only: bool
    allow_global_access: bool
    max_steps: int
    verbose: bool
    transcript_path: Optional[Path]
    tavily_api_key: str
    execution_mode: ExecutionMode = ExecutionMode.UNRESTRICTED  # Default to unrestricted
    parallel_tools: bool = True  # Enable parallel tool execution
    auto_approve: bool = True  # Auto-approve all operations without prompting
    stream_output: bool = True  # Stream command outputs in real-time
    enable_reasoning: bool = True  # Enable reasoning/thinking display


@dataclass
class ToolExecutor:
    """Enhanced tool executor with unrestricted capabilities."""

    root: Path
    encoding: str = "utf-8"
    read_only: bool = False
    allow_global_access: bool = True
    tavily_api_key: Optional[str] = None
    execution_mode: ExecutionMode = ExecutionMode.UNRESTRICTED
    auto_approve: bool = True
    stream_output: bool = True
    _active_processes: Dict[str, subprocess.Popen] = field(default_factory=dict)

    def list_dir(self, path: str = ".", recursive: bool = False) -> ToolResult:
        target = _ensure_within_root(self.root, path, self.allow_global_access)
        if not target.exists():
            return f"Path '{path}' does not exist."

        def iter_entries(base: Path, depth: int = 0) -> Iterable[str]:
            if depth > MAX_LIST_DEPTH:
                yield "    " * depth + "… (max depth reached)"
                return
            entries = sorted(base.iterdir(), key=lambda p: (p.is_file(), p.name.lower()))
            for entry in entries:
                marker = "/" if entry.is_dir() else ""
                yield "    " * depth + entry.name + marker
                if recursive and entry.is_dir():
                    yield from iter_entries(entry, depth + 1)

        lines = [f"Listing for {target.relative_to(self.root) if target != self.root else '.'}:"]
        lines.extend(iter_entries(target))
        return "\n".join(lines)

    def read_file(self, path: str, offset: int = 0, limit: Optional[int] = None) -> ToolResult:
        target = _ensure_within_root(self.root, path, self.allow_global_access)
        if not target.exists():
            return f"File '{path}' does not exist."
        if not target.is_file():
            return f"Path '{path}' is not a file."

        text = target.read_text(encoding=self.encoding)
        if offset:
            text = text[offset:]
        if limit is not None:
            text = text[:limit]
        return text

    def write_file(self, path: str, content: str, create_parents: bool = False) -> ToolResult:
        if self.read_only:
            return "Write operations are disabled (read-only mode)."
        target = _ensure_within_root(self.root, path, self.allow_global_access)
        if create_parents:
            target.parent.mkdir(parents=True, exist_ok=True)
        if not target.parent.exists():
            return (
                f"Cannot write '{path}': parent directory does not exist. "
                "Pass create_parents=true to create it."
            )
        existing_mode: Optional[int] = None
        if target.exists():
            try:
                existing_mode = stat.S_IMODE(target.stat().st_mode)
            except OSError:
                existing_mode = None
        fd = None
        tmp_path: Optional[Path] = None
        try:
            fd, tmp_name = tempfile.mkstemp(dir=str(target.parent))
            tmp_path = Path(tmp_name)
            with os.fdopen(fd, "w", encoding=self.encoding) as handle:
                fd = None
                handle.write(content)
            desired_mode = existing_mode if existing_mode is not None else _default_file_mode()
            try:
                os.chmod(tmp_path, desired_mode)
            except OSError:
                # Ignore chmod errors; proceed with replacement
                pass
            tmp_path.replace(target)
        except Exception as exc:
            if fd is not None:
                os.close(fd)
            if tmp_path and tmp_path.exists():
                try:
                    tmp_path.unlink()
                except OSError:
                    pass
            return f"Failed to write '{path}': {exc}"
        return f"Wrote {len(content)} characters to '{path}'."

    def todo_write(
        self,
        item: str,
        path: str = "TODO.md",
        heading: Optional[str] = None,
        timestamp: bool = True,
        create_parents: bool = True,
    ) -> ToolResult:
        """Append checklist entries, mirroring Claude Code's TodoWrite helper."""
        if self.read_only:
            return "Todo updates are disabled (read-only mode)."
        entry = (item or "").strip()
        if not entry:
            return "Todo entry must not be empty."
        target = _ensure_within_root(self.root, path, self.allow_global_access)
        if create_parents:
            target.parent.mkdir(parents=True, exist_ok=True)
        lines: List[str] = []
        if heading:
            lines.append(f"## {heading.strip()}\n")
        prefix = "- "
        if timestamp:
            prefix += datetime.now().strftime("[%Y-%m-%d %H:%M] ")
        lines.append(f"{prefix}{entry}\n")
        try:
            with target.open("a", encoding=self.encoding) as handle:
                for line in lines:
                    handle.write(line)
        except OSError as exc:
            return f"Failed to append todo entry: {exc}"
        display_path = _format_path_for_display(self.root, target, self.allow_global_access)
        return f"Added todo entry to '{display_path}'."

    def move_path(
        self,
        source: str,
        destination: str,
        overwrite: bool = False,
        create_parents: bool = False,
    ) -> ToolResult:
        if self.read_only:
            return "Move operations are disabled (read-only mode)."
        try:
            src_path = _ensure_within_root(self.root, source, self.allow_global_access)
            dest_path = _resolve_path(self.root, destination, allow_global=self.allow_global_access)
        except ValueError as exc:
            return str(exc)
        if not src_path.exists():
            return f"Source '{source}' does not exist."

        target_path = dest_path
        if dest_path.exists() and dest_path.is_dir():
            target_path = dest_path / src_path.name

        if target_path == src_path:
            return "Source and destination resolve to the same location."

        parent = target_path.parent
        if not parent.exists():
            if create_parents:
                try:
                    parent.mkdir(parents=True, exist_ok=True)
                except Exception as exc:
                    return f"Failed to create parent directories for '{destination}': {exc}"
            else:
                return (
                    f"Destination parent directory '{parent}' does not exist. "
                    "Pass create_parents=true to create it."
                )

        if target_path.exists():
            if not overwrite:
                return (
                    f"Destination '{destination}' already exists. "
                    "Pass overwrite=true to replace it."
                )
            try:
                if target_path.is_dir() and not target_path.is_symlink():
                    shutil.rmtree(target_path)
                else:
                    target_path.unlink()
            except Exception as exc:
                return f"Unable to replace existing destination '{destination}': {exc}"

        try:
            shutil.move(str(src_path), str(target_path))
        except Exception as exc:
            return f"Failed to move '{source}' to '{destination}': {exc}"

        display_path = _format_path_for_display(self.root, target_path, self.allow_global_access)
        return f"Moved '{source}' to '{display_path}'."

    def stat_path(self, path: str = ".") -> ToolResult:
        target = _ensure_within_root(self.root, path, self.allow_global_access)
        if not target.exists():
            return f"Path '{path}' does not exist."
        stats = target.stat()
        info = {
            "path": str(target.relative_to(self.root)),
            "type": "directory" if target.is_dir() else "file" if target.is_file() else "other",
            "size": stats.st_size,
            "modified": datetime.fromtimestamp(stats.st_mtime).isoformat(),
        }
        if target.is_symlink():
            info["symlink_target"] = os.readlink(target)
        return json.dumps(info, indent=2)

    def search_text(
        self,
        pattern: str,
        path: str = ".",
        case_sensitive: bool = True,
        max_results: int = 200,
    ) -> ToolResult:
        target = _ensure_within_root(self.root, path, self.allow_global_access)
        if not target.exists():
            return f"Search path '{path}' does not exist."
        if not pattern:
            return "Search pattern must not be empty."
        use_rg = shutil.which("rg") is not None
        if use_rg:
            cmd = ["rg", "--line-number", "--color", "never"]
            if not case_sensitive:
                cmd.append("-i")
            cmd.extend(["--max-count", str(max_results), pattern, str(target)])
        else:
            cmd = ["grep", "-R", "-n", "-I"]
            if not case_sensitive:
                cmd.append("-i")
            cmd.extend([pattern, str(target)])
        try:
            proc = subprocess.run(
                cmd,
                text=True,
                capture_output=True,
                cwd=self.root,
            )
        except FileNotFoundError:
            return "Neither ripgrep nor grep is available on this system."
        stdout = proc.stdout.strip()
        stderr = proc.stderr.strip()
        if proc.returncode not in (0, 1):
            return f"Search command failed (exit {proc.returncode}).\n{stderr}"
        if not stdout:
            return "No matches found."
        lines = stdout.splitlines()
        truncated = ""
        if len(lines) > max_results:
            lines = lines[:max_results]
            truncated = f"\n… truncated to {max_results} results."
        result = "\n".join(lines) + truncated
        if stderr:
            result += f"\n[stderr]\n{stderr}"
        return result

    def apply_patch(self, patch: str) -> ToolResult:
        if self.read_only:
            return "Patch operations are disabled (read-only mode)."
        if not patch.strip():
            return "Patch content is empty."

        def _safe_path(text: str) -> bool:
            if self.allow_global_access:
                return True
            text = text.strip()
            if text in {"/dev/null", "a/", "b/"}:
                return True
            prefixes = ("a/", "b/", "c/")
            for prefix in prefixes:
                if text.startswith(prefix):
                    text = text[len(prefix):]
                    break
            if text.startswith("/"):
                return False
            parts = Path(text).parts
            return ".." not in parts

        for line in patch.splitlines():
            if line.startswith(("+++", "---")):
                tokens = line.split(maxsplit=1)
                if len(tokens) == 2 and not _safe_path(tokens[1]):
                    return f"Unsafe path detected in patch header: {tokens[1]}"
        patch_cmd = shutil.which("patch")
        patch_level = 1 if any(line.startswith("diff --git") for line in patch.splitlines()) else 0
        if patch_cmd:
            proc = subprocess.run(
                [patch_cmd, f"-p{patch_level}", "--batch", "--silent"],
                input=patch,
                text=True,
                capture_output=True,
                cwd=self.root,
            )
        else:
            git_cmd = shutil.which("git")
            if not git_cmd:
                return "No patch utility available (missing both patch and git)."
            proc = subprocess.run(
                [git_cmd, "apply", "--whitespace=nowarn", f"-p{patch_level}"],
                input=patch,
                text=True,
                capture_output=True,
                cwd=self.root,
            )
        stdout = proc.stdout.strip()
        stderr = proc.stderr.strip()
        if proc.returncode != 0:
            message = stderr or "Patch command failed"
            return f"Patch failed (exit {proc.returncode}).\n{message}"
        response_lines = ["Patch applied successfully."]
        if stdout:
            response_lines.append(stdout)
        if stderr:
            response_lines.append(f"[stderr]\n{stderr}")
        return "\n".join(response_lines)

    def run_shell(self, command: str, timeout: int = 120, background: bool = False,
                  shell_id: Optional[str] = None) -> ToolResult:
        """Execute shell commands with no permission checks in unrestricted mode."""
        if not command.strip():
            return "Command is empty."

        # In unrestricted mode, execute immediately without any prompts
        if self.execution_mode == ExecutionMode.UNRESTRICTED:
            if background:
                # Run command in background
                shell_id = shell_id or f"shell_{time.time()}"
                try:
                    proc = subprocess.Popen(
                        ["/bin/bash", "-lc", command],
                        cwd=self.root,
                        text=True,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        stdin=subprocess.PIPE,
                    )
                    self._active_processes[shell_id] = proc
                    return f"Command started in background with ID: {shell_id}\nUse get_shell_output('{shell_id}') to check status."
                except Exception as e:
                    return f"Failed to start background command: {e}"

            # Stream output if enabled
            if self.stream_output:
                try:
                    proc = subprocess.Popen(
                        ["/bin/bash", "-lc", command],
                        cwd=self.root,
                        text=True,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        bufsize=1,
                        universal_newlines=True
                    )

                    output_lines = [f"$ {command}"]
                    for line in iter(proc.stdout.readline, ''):
                        if line:
                            output_lines.append(line.rstrip())
                            if len(output_lines) > 1000:  # Limit output size
                                output_lines = output_lines[-900:]
                                output_lines.insert(0, "... (output truncated) ...")

                    proc.wait(timeout=timeout)
                    output_lines.append(f"[exit {proc.returncode}]")
                    return "\n".join(output_lines)

                except subprocess.TimeoutExpired:
                    proc.kill()
                    return f"Command timed out after {timeout} seconds."
                except Exception as e:
                    return f"Command execution failed: {e}"
            else:
                # Non-streaming execution
                try:
                    proc = subprocess.run(
                        ["/bin/bash", "-lc", command],
                        cwd=self.root,
                        text=True,
                        capture_output=True,
                        timeout=timeout,
                    )
                except subprocess.TimeoutExpired:
                    return f"Command timed out after {timeout} seconds."

                stdout = proc.stdout.strip()
                stderr = proc.stderr.strip()
                lines = [f"$ {command}"]
                if stdout:
                    lines.append(stdout)
                if stderr:
                    lines.append("[stderr]\n" + stderr)
                lines.append(f"[exit {proc.returncode}]")
                return "\n".join(lines)

        # For non-unrestricted modes, use original implementation
        try:
            proc = subprocess.run(
                ["/bin/bash", "-lc", command],
                cwd=self.root,
                text=True,
                capture_output=True,
                timeout=timeout,
            )
        except subprocess.TimeoutExpired:
            return f"Command timed out after {timeout} seconds."
        stdout = proc.stdout.strip()
        stderr = proc.stderr.strip()
        lines = [f"$ {command}"]
        if stdout:
            lines.append(stdout)
        if stderr:
            lines.append("[stderr]\n" + stderr)
        lines.append(f"[exit {proc.returncode}]")
        return "\n".join(lines)

    def python_repl(self, code: str, timeout: int = 120) -> ToolResult:
        if not code.strip():
            return "Code snippet is empty."
        try:
            proc = subprocess.run(
                [sys.executable, "-c", code],
                cwd=self.root,
                text=True,
                capture_output=True,
                timeout=timeout,
            )
        except subprocess.TimeoutExpired:
            return f"Python execution timed out after {timeout} seconds."
        stdout = proc.stdout.strip()
        stderr = proc.stderr.strip()
        lines = ["python -c <<'PY'", code, "PY"]
        if stdout:
            lines.append(stdout)
        if stderr:
            lines.append("[stderr]\n" + stderr)
        lines.append(f"[exit {proc.returncode}]")
        return "\n".join(lines)

    def tavily_search(
        self,
        query: str,
        search_depth: str = "basic",
        max_results: int = 5,
        api_key: Optional[str] = None,
    ) -> ToolResult:
        cleaned_query = (query or "").strip()
        if not cleaned_query:
            return "Search query must not be empty."
        depth = (search_depth or "basic").lower()
        if depth not in {"basic", "advanced"}:
            depth = "basic"
        try:
            limit = int(max_results)
        except (TypeError, ValueError):
            limit = 5
        limit = max(1, min(limit, 10))
        key = (api_key or self.tavily_api_key or DEFAULT_TAVILY_API_KEY or "").strip()
        if not key:
            key = DEFAULT_TAVILY_API_KEY
        request_payload = {
            "api_key": key,
            "query": cleaned_query,
            "search_depth": depth,
            "max_results": limit,
        }
        request = urllib.request.Request(
            "https://api.tavily.com/search",
            data=json.dumps(request_payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                body = response.read().decode("utf-8", errors="replace")
        except urllib.error.HTTPError as exc:
            try:
                error_body = exc.read().decode("utf-8", errors="replace")
            except Exception:
                error_body = ""
            if exc.code in {401, 403}:
                instructions = (
                    f"Tavily rejected the request (HTTP {exc.code}). "
                    "Provide a valid Tavily API key via `deepseek config set tavily_api_key YOUR_KEY` "
                    "or the interactive @tavily command."
                )
                if error_body:
                    return instructions + f"\nResponse body:\n{error_body}"
                return instructions
            details = f"\nResponse body:\n{error_body}" if error_body else ""
            return f"Tavily search failed (HTTP {exc.code}).{details}"
        except urllib.error.URLError as exc:
            return f"Tavily search failed: {exc}"
        except Exception as exc:  # pragma: no cover - unexpected runtime issues
            return f"Tavily search encountered an unexpected error: {exc}"
        try:
            payload = json.loads(body)
        except json.JSONDecodeError:
            return f"Tavily response was not valid JSON:\n{body}"

        lines: List[str] = []
        answer = payload.get("answer")
        if answer:
            lines.append(f"Answer: {answer}")
        results = payload.get("results") or []
        if results:
            for index, item in enumerate(results[:limit], start=1):
                title = item.get("title") or item.get("url") or f"Result {index}"
                url = item.get("url") or ""
                snippet = (item.get("content") or item.get("snippet") or "").strip()
                if len(snippet) > 500:
                    snippet = snippet[:500] + "…"
                entry_parts = [f"{index}. {title}"]
                if url:
                    entry_parts.append(url)
                if snippet:
                    entry_parts.append(snippet)
                lines.append("\n".join(entry_parts))
        else:
            lines.append("No Tavily results returned.")

        related = payload.get("related_questions") or []
        if related:
            lines.append("Related questions: " + "; ".join(related[:5]))

        return "\n\n".join(lines)

    def tavily_extract(
        self,
        url: str,
        extract_depth: str = "basic",
        max_pages: int = 1,
        summary: bool = True,
        api_key: Optional[str] = None,
    ) -> ToolResult:
        """Fetch structured documentation via Tavily's extract endpoint."""
        cleaned_url = (url or "").strip()
        if not cleaned_url:
            return "URL must not be empty."
        depth = (extract_depth or "basic").lower()
        if depth not in {"basic", "advanced"}:
            depth = "basic"
        try:
            pages = int(max_pages)
        except (TypeError, ValueError):
            pages = 1
        pages = max(1, min(pages, 5))
        key = (api_key or self.tavily_api_key or DEFAULT_TAVILY_API_KEY or "").strip()
        if not key:
            key = DEFAULT_TAVILY_API_KEY
        request_payload = {
            "api_key": key,
            "url": cleaned_url,
            "extract_depth": depth,
            "max_pages": pages,
            "include_images": False,
            "summary": bool(summary),
        }
        request = urllib.request.Request(
            "https://api.tavily.com/extract",
            data=json.dumps(request_payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                body = response.read().decode("utf-8", errors="replace")
        except urllib.error.HTTPError as exc:
            try:
                error_body = exc.read().decode("utf-8", errors="replace")
            except Exception:
                error_body = ""
            if exc.code in {401, 403}:
                instructions = (
                    f"Tavily extract rejected the request (HTTP {exc.code}). "
                    "Provide a valid Tavily API key via `deepseek config set tavily_api_key YOUR_KEY`."
                )
                if error_body:
                    return instructions + f"\nResponse body:\n{error_body}"
                return instructions
            details = f"\nResponse body:\n{error_body}" if error_body else ""
            return f"Tavily extract failed (HTTP {exc.code}).{details}"
        except urllib.error.URLError as exc:
            return f"Tavily extract failed: {exc}"
        except Exception as exc:  # pragma: no cover
            return f"Tavily extract encountered an unexpected error: {exc}"
        try:
            payload = json.loads(body)
        except json.JSONDecodeError:
            return f"Tavily extract response was not valid JSON:\n{body}"

        title = payload.get("title") or cleaned_url
        summary_text = payload.get("summary")
        content = payload.get("content") or payload.get("results") or []
        sections: List[str] = []
        sections.append(f"# {title}")
        if summary_text:
            sections.append(summary_text.strip())
        if isinstance(content, list):
            for idx, chunk in enumerate(content, start=1):
                chunk_title = chunk.get("title") or f"Section {idx}"
                chunk_content = (chunk.get("content") or "").strip()
                if not chunk_content:
                    continue
                sections.append(f"## {chunk_title}\n{chunk_content}")
        elif isinstance(content, str):
            sections.append(content.strip())
        else:
            sections.append("No structured content returned.")
        return "\n\n".join(part for part in sections if part.strip())

    def http_request(
        self,
        url: str,
        method: str = "GET",
        headers: Optional[Dict[str, str]] = None,
        body: Optional[str] = None,
        timeout: int = 30,
    ) -> ToolResult:
        if not url.strip():
            return "URL must not be empty."
        request = urllib.request.Request(url, method=method.upper())
        for key, value in (headers or {}).items():
            request.add_header(key, value)
        if body is not None:
            request.data = body.encode("utf-8")
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                content = response.read().decode("utf-8", errors="replace")
                header_lines = "\n".join(f"{k}: {v}" for k, v in response.headers.items())
                result_lines = [
                    f"{request.method} {url} -> {response.status}",
                    header_lines,
                    "",
                    content,
                ]
                return "\n".join(line for line in result_lines if line is not None)
        except urllib.error.URLError as exc:
            return f"HTTP request failed: {exc}"

    def get_shell_output(self, shell_id: str) -> ToolResult:
        """Get output from a background shell process."""
        proc = self._active_processes.get(shell_id)
        if not proc:
            return f"No process found with ID: {shell_id}"

        # Check if process is still running
        poll_result = proc.poll()
        if poll_result is None:
            # Still running - get partial output
            try:
                output, _ = proc.communicate(timeout=0.1)
                return f"Process {shell_id} still running...\nPartial output:\n{output}"
            except subprocess.TimeoutExpired:
                return f"Process {shell_id} is still running (no new output available)"
        else:
            # Process finished
            output, error = proc.communicate()
            del self._active_processes[shell_id]
            result = f"Process {shell_id} completed with exit code {poll_result}\n"
            if output:
                result += f"Output:\n{output}\n"
            if error:
                result += f"Errors:\n{error}\n"
            return result

    def kill_shell(self, shell_id: str) -> ToolResult:
        """Kill a background shell process."""
        proc = self._active_processes.get(shell_id)
        if not proc:
            return f"No process found with ID: {shell_id}"

        try:
            proc.terminate()
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait()

        del self._active_processes[shell_id]
        return f"Process {shell_id} has been terminated."

    def git_operation(self, operation: str, args: List[str] = None) -> ToolResult:
        """Execute git operations without permission checks."""
        if self.execution_mode != ExecutionMode.UNRESTRICTED and self.read_only:
            return "Git operations are disabled in read-only mode."

        git_cmd = shutil.which("git")
        if not git_cmd:
            return "Git is not available on this system."

        valid_operations = [
            "status", "log", "diff", "add", "commit", "push", "pull",
            "checkout", "branch", "merge", "rebase", "stash", "clone",
            "fetch", "reset", "tag", "remote"
        ]

        if operation not in valid_operations:
            return f"Invalid git operation: {operation}. Valid operations: {', '.join(valid_operations)}"

        cmd = [git_cmd, operation]
        if args:
            cmd.extend(args)

        try:
            proc = subprocess.run(
                cmd,
                cwd=self.root,
                text=True,
                capture_output=True,
                timeout=60,
            )
            stdout = proc.stdout.strip()
            stderr = proc.stderr.strip()

            result_lines = [f"$ git {operation} {' '.join(args or [])}"]
            if stdout:
                result_lines.append(stdout)
            if stderr:
                result_lines.append(f"[stderr]\n{stderr}")
            result_lines.append(f"[exit {proc.returncode}]")

            return "\n".join(result_lines)
        except subprocess.TimeoutExpired:
            return f"Git operation timed out after 60 seconds."
        except Exception as e:
            return f"Git operation failed: {e}"

    def docker_operation(self, operation: str, args: List[str] = None) -> ToolResult:
        """Execute docker operations without permission checks."""
        if self.execution_mode != ExecutionMode.UNRESTRICTED:
            return "Docker operations require unrestricted execution mode."

        docker_cmd = shutil.which("docker")
        if not docker_cmd:
            return "Docker is not available on this system."

        valid_operations = [
            "ps", "images", "run", "exec", "stop", "start", "restart",
            "rm", "rmi", "build", "push", "pull", "logs", "inspect",
            "compose", "network", "volume"
        ]

        if operation not in valid_operations:
            return f"Invalid docker operation: {operation}. Valid operations: {', '.join(valid_operations)}"

        cmd = [docker_cmd, operation]
        if args:
            cmd.extend(args)

        try:
            proc = subprocess.run(
                cmd,
                text=True,
                capture_output=True,
                timeout=120,
            )
            stdout = proc.stdout.strip()
            stderr = proc.stderr.strip()

            result_lines = [f"$ docker {operation} {' '.join(args or [])}"]
            if stdout:
                result_lines.append(stdout)
            if stderr and proc.returncode != 0:
                result_lines.append(f"[stderr]\n{stderr}")
            result_lines.append(f"[exit {proc.returncode}]")

            return "\n".join(result_lines)
        except subprocess.TimeoutExpired:
            return f"Docker operation timed out after 120 seconds."
        except Exception as e:
            return f"Docker operation failed: {e}"

    def system_info(self) -> ToolResult:
        """Get comprehensive system information."""
        info = {}

        # Platform info
        info['platform'] = sys.platform
        info['python_version'] = sys.version

        # OS info
        try:
            import platform
            info['os'] = platform.system()
            info['os_release'] = platform.release()
            info['machine'] = platform.machine()
            info['processor'] = platform.processor()
        except Exception:
            pass

        # CPU info
        try:
            if sys.platform == "darwin":
                cpu_info = subprocess.check_output(["sysctl", "-n", "machdep.cpu.brand_string"], text=True).strip()
                info['cpu'] = cpu_info
            elif sys.platform == "linux":
                with open('/proc/cpuinfo') as f:
                    for line in f:
                        if line.startswith('model name'):
                            info['cpu'] = line.split(':')[1].strip()
                            break
        except Exception:
            pass

        # Memory info
        try:
            if sys.platform == "darwin":
                mem_info = subprocess.check_output(["sysctl", "-n", "hw.memsize"], text=True).strip()
                info['memory'] = f"{int(mem_info) / (1024**3):.2f} GB"
            elif sys.platform == "linux":
                with open('/proc/meminfo') as f:
                    for line in f:
                        if line.startswith('MemTotal'):
                            mem_kb = int(line.split()[1])
                            info['memory'] = f"{mem_kb / (1024**2):.2f} GB"
                            break
        except Exception:
            pass

        # Disk info
        try:
            df_output = subprocess.check_output(["df", "-h", str(self.root)], text=True)
            lines = df_output.strip().split('\n')
            if len(lines) > 1:
                info['disk_usage'] = lines[1]
        except Exception:
            pass

        return json.dumps(info, indent=2)

    def download_file(
        self,
        url: str,
        destination: str,
        overwrite: bool = False,
        create_parents: bool = False,
        mode: str = "binary",
        timeout: int = 120,
    ) -> ToolResult:
        if self.read_only:
            return "Download operations are disabled (read-only mode)."
        cleaned_url = (url or "").strip()
        if not cleaned_url:
            return "URL must not be empty."
        try:
            dest_path = _ensure_within_root(self.root, destination, self.allow_global_access)
        except ValueError as exc:
            return str(exc)

        if dest_path.exists() and dest_path.is_dir():
            filename = Path(urllib.parse.urlparse(cleaned_url).path).name or "downloaded_file"
            dest_path = dest_path / filename

        parent = dest_path.parent
        if not parent.exists():
            if create_parents:
                try:
                    parent.mkdir(parents=True, exist_ok=True)
                except Exception as exc:
                    return f"Failed to create parent directories for '{destination}': {exc}"
            else:
                return (
                    f"Destination parent directory '{parent}' does not exist. "
                    "Pass create_parents=true to create it."
                )

        if dest_path.exists():
            if not overwrite:
                return (
                    f"Destination '{destination}' already exists. "
                    "Pass overwrite=true to replace it."
                )
            try:
                if dest_path.is_dir() and not dest_path.is_symlink():
                    shutil.rmtree(dest_path)
                else:
                    dest_path.unlink()
            except Exception as exc:
                return f"Unable to replace existing destination '{destination}': {exc}"

        request = urllib.request.Request(cleaned_url)
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                payload = response.read()
        except urllib.error.URLError as exc:
            return f"Download failed: {exc}"
        except Exception as exc:
            return f"Download encountered an unexpected error: {exc}"

        try:
            if mode.lower() == "text":
                dest_path.write_text(payload.decode(self.encoding), encoding=self.encoding)
            else:
                dest_path.write_bytes(payload)
        except Exception as exc:
            return f"Failed to write downloaded content to '{destination}': {exc}"

        display_path = _format_path_for_display(self.root, dest_path, self.allow_global_access)
        return f"Downloaded {len(payload)} bytes from '{cleaned_url}' to '{display_path}'."


def _ensure_within_root(root: Path, path: str, allow_global: bool) -> Path:
    return _resolve_path(root, path, allow_global=allow_global)


def _resolve_path(root: Path, path: str, allow_global: bool) -> Path:
    raw = Path(path).expanduser()
    if raw.is_absolute():
        candidate = raw.resolve()
    else:
        candidate = (root / raw).resolve()
    if not allow_global:
        try:
            candidate.relative_to(root)
        except ValueError as exc:
            raise ValueError(f"Path '{path}' escapes the workspace root") from exc
    return candidate


def _format_path_for_display(root: Path, path: Path, allow_global: bool) -> str:
    if allow_global:
        return str(path)
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


class LiveThoughtDisplay:
    """Enhanced display with reasoning support and better formatting."""

    def __init__(self, console: Console, start_time: float, enable_reasoning: bool = True):
        self.console = console
        self._start_time = start_time
        self._live = Live(Text(""), console=console, refresh_per_second=8, transient=False)
        self._message: str = ""
        self._style: str = "bright_blue"
        self._file_ops: Dict[str, int] = {}
        self._enable_reasoning = enable_reasoning
        self._reasoning_buffer: List[str] = []
        self._current_tool: Optional[str] = None
        self._current_plan: str = ""

    def __enter__(self) -> "LiveThoughtDisplay":
        self._live.__enter__()
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self._live.__exit__(exc_type, exc, tb)

    def update_thought(
        self,
        message: str,
        *,
        style: str = "bright_blue",
        file_ops: Optional[Mapping[str, int]] = None,
    ) -> None:
        self._message = message
        self._style = style
        if file_ops is not None:
            self._file_ops = {key: value for key, value in file_ops.items() if value}
        self._render()

    def show_reasoning(self, text: str) -> None:
        """Display reasoning/thinking process."""
        if self._enable_reasoning:
            self._reasoning_buffer.append(text)
            # Show condensed reasoning in dim style
            self.console.print(f"[dim]💭 {text[:100]}{'...' if len(text) > 100 else ''}[/dim]")

    def show_tool_execution(self, tool_name: str, args: Dict[str, Any]) -> None:
        """Display tool execution with nice formatting."""
        self._current_tool = tool_name
        args_str = json.dumps(args, indent=2) if args else "{}"

        # Use icons for different tool categories
        tool_icons = {
            "run_shell": "🖥️",
            "git_operation": "🔀",
            "docker_operation": "🐳",
            "write_file": "📝",
            "todo_write": "✅",
            "read_file": "📖",
            "list_dir": "📁",
            "search_text": "🔍",
            "tavily_search": "🌐",
            "tavily_extract": "📚",
            "python_repl": "🐍",
            "system_info": "ℹ️",
            "http_request": "🌍",
            "download_file": "⬇️",
        }

        icon = tool_icons.get(tool_name, "🔧")
        self.console.print(
            Panel(
                f"[cyan]{icon} Executing: {tool_name}[/cyan]\n[dim]{args_str}[/dim]",
                border_style="cyan",
                padding=(0, 1),
            )
        )

    def show_plan(self, plan_lines: Sequence[str]) -> None:
        """Render the agent's current action plan when it changes."""
        if not self._enable_reasoning or not plan_lines:
            return
        plan_text = "\n".join(plan_lines).strip()
        if not plan_text or plan_text == self._current_plan:
            return
        self._current_plan = plan_text
        panel = Panel(
            plan_text,
            title="Working Plan",
            border_style="magenta",
            padding=(0, 1),
        )
        self.console.print(panel)

    def update_file_ops(self, file_ops: Mapping[str, int]) -> None:
        self._file_ops = {key: value for key, value in file_ops.items() if value}
        self._render()

    def persist(self, message: str) -> None:
        self._live.console.print(Text(message))
        self._live.refresh()

    def clear(self) -> None:
        self._live.update(Text(""), refresh=True)
        self._message = ""
        self._file_ops = {}
        self._style = "bright_blue"

    def _render(self) -> None:
        elapsed = time.perf_counter() - self._start_time
        header = f"[bold bright_blue]▌[/] [{self._style}]{self._message}[/{self._style}]"
        ops_markup = self._format_file_ops()
        if ops_markup:
            header += f" [dim]|[/] [cyan]{ops_markup}[/cyan]"
        footer = f"[dim]Elapsed {elapsed:5.1f}s since start[/]"
        markup = header + "\n" + footer
        self._live.update(Text.from_markup(markup), refresh=True)

    def _format_file_ops(self) -> str:
        if not self._file_ops:
            return ""
        preferred_order = ("list_dir", "read_file", "stat_path", "write_file")
        parts: List[str] = []
        for name in preferred_order:
            count = self._file_ops.get(name)
            if not count:
                continue
            label = name.replace("_", " ")
            if count > 1:
                label = f"{label}×{count}"
            parts.append(label)
        remaining = sorted(
            (key for key in self._file_ops.keys() if key not in preferred_order),
        )
        for name in remaining:
            count = self._file_ops[name]
            label = name.replace("_", " ")
            if count > 1:
                label = f"{label}×{count}"
            parts.append(label)
        return " · ".join(parts)


def _format_file_ops_for_console(file_ops: Mapping[str, int]) -> str:
    active = {key: value for key, value in file_ops.items() if value}
    if not active:
        return ""
    preferred_order = ("list_dir", "read_file", "stat_path", "write_file")
    parts: List[str] = []
    for name in preferred_order:
        count = active.get(name)
        if not count:
            continue
        label = name.replace("_", " ")
        if count > 1:
            label = f"{label}×{count}"
        parts.append(label)
    remaining = sorted(name for name in active if name not in preferred_order)
    for name in remaining:
        count = active[name]
        label = name.replace("_", " ")
        if count > 1:
            label = f"{label}×{count}"
        parts.append(label)
    return " · ".join(parts)


def tool_schemas() -> List[Dict[str, Any]]:
    """Return enhanced tool schemas including new capabilities."""
    return [
        {
            "type": "function",
            "function": {
                "name": "list_dir",
                "description": "List files and directories relative to the workspace root.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "default": "."},
                        "recursive": {"type": "boolean", "default": False},
                    },
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "read_file",
                "description": "Read file contents from the repository.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string"},
                        "offset": {"type": "integer", "minimum": 0, "default": 0},
                        "limit": {"type": "integer", "minimum": 1},
                    },
                    "required": ["path"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "write_file",
                "description": "Write full file contents to a path within the repository.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string"},
                        "content": {"type": "string"},
                        "create_parents": {"type": "boolean", "default": False},
                    },
                    "required": ["path", "content"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "todo_write",
                "description": "Append an item to a TODO.md style checklist.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "item": {"type": "string"},
                        "path": {"type": "string", "default": "TODO.md"},
                        "heading": {"type": "string"},
                        "timestamp": {"type": "boolean", "default": True},
                        "create_parents": {"type": "boolean", "default": True},
                    },
                    "required": ["item"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "move_path",
                "description": "Move or rename files and directories.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "source": {"type": "string"},
                        "destination": {"type": "string"},
                        "overwrite": {"type": "boolean", "default": False},
                        "create_parents": {"type": "boolean", "default": False},
                    },
                    "required": ["source", "destination"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "stat_path",
                "description": "Return metadata about a file or directory.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "default": "."},
                    },
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "search_text",
                "description": "Search for text within the repository using ripgrep or grep.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "pattern": {"type": "string"},
                        "path": {"type": "string", "default": "."},
                        "case_sensitive": {"type": "boolean", "default": True},
                        "max_results": {"type": "integer", "default": 200, "minimum": 1},
                    },
                    "required": ["pattern"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "apply_patch",
                "description": "Apply a unified diff patch to workspace files.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "patch": {"type": "string"},
                    },
                    "required": ["patch"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "run_shell",
                "description": "Execute a shell command from the workspace root.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "command": {"type": "string"},
                        "timeout": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": 600,
                            "default": 120,
                        },
                    },
                    "required": ["command"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "python_repl",
                "description": "Execute a Python snippet using the system interpreter.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "code": {"type": "string"},
                        "timeout": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": 600,
                            "default": 120,
                        },
                    },
                    "required": ["code"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "http_request",
                "description": "Perform an HTTP request (GET/POST/etc.) and return the response.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "url": {"type": "string"},
                        "method": {"type": "string", "default": "GET"},
                        "headers": {"type": "object"},
                        "body": {"type": "string"},
                        "timeout": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": 120,
                            "default": 30,
                        },
                    },
                    "required": ["url"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "download_file",
                "description": "Download remote content and save it to disk.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "url": {"type": "string"},
                        "destination": {"type": "string"},
                        "overwrite": {"type": "boolean", "default": False},
                        "create_parents": {"type": "boolean", "default": False},
                        "mode": {
                            "type": "string",
                            "enum": ["binary", "text"],
                            "default": "binary",
                        },
                        "timeout": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": 600,
                            "default": 120,
                        },
                    },
                    "required": ["url", "destination"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "tavily_search",
                "description": "Search the web using Tavily's API and summarize the results.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string"},
                        "search_depth": {
                            "type": "string",
                            "enum": ["basic", "advanced"],
                            "default": "basic",
                        },
                        "max_results": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": 10,
                            "default": 5,
                        },
                        "api_key": {
                            "type": "string",
                            "description": "Override the Tavily API key for this request.",
                        },
                    },
                    "required": ["query"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "tavily_extract",
                "description": "Fetch structured documentation from a URL via Tavily extract.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "url": {"type": "string"},
                        "extract_depth": {
                            "type": "string",
                            "enum": ["basic", "advanced"],
                            "default": "basic",
                        },
                        "max_pages": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": 5,
                            "default": 1,
                        },
                        "summary": {"type": "boolean", "default": True},
                        "api_key": {
                            "type": "string",
                            "description": "Override the Tavily API key for this request.",
                        },
                    },
                    "required": ["url"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "git_operation",
                "description": "Execute git operations like status, commit, push, etc.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "operation": {
                            "type": "string",
                            "enum": ["status", "log", "diff", "add", "commit", "push", "pull",
                                    "checkout", "branch", "merge", "rebase", "stash", "clone",
                                    "fetch", "reset", "tag", "remote"],
                        },
                        "args": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Additional arguments for the git command",
                        },
                    },
                    "required": ["operation"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "docker_operation",
                "description": "Execute docker operations like ps, run, build, etc.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "operation": {
                            "type": "string",
                            "enum": ["ps", "images", "run", "exec", "stop", "start", "restart",
                                    "rm", "rmi", "build", "push", "pull", "logs", "inspect",
                                    "compose", "network", "volume"],
                        },
                        "args": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Additional arguments for the docker command",
                        },
                    },
                    "required": ["operation"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_shell_output",
                "description": "Get output from a background shell process.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "shell_id": {"type": "string", "description": "ID of the background shell process"},
                    },
                    "required": ["shell_id"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "kill_shell",
                "description": "Kill a background shell process.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "shell_id": {"type": "string", "description": "ID of the background shell process to kill"},
                    },
                    "required": ["shell_id"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "system_info",
                "description": "Get comprehensive system information including OS, CPU, memory, and disk usage.",
                "parameters": {
                    "type": "object",
                    "properties": {},
                },
            },
        },
    ]


def execute_tool(executor: ToolExecutor, name: str, arguments: Dict[str, Any]) -> ToolResult:
    func: Callable[..., ToolResult]
    try:
        func = getattr(executor, name)
    except AttributeError as exc:
        raise ValueError(f"Unknown tool '{name}'.") from exc
    return func(**arguments)


def build_messages(system_prompt: str, user_prompt: str, follow_up: List[str]) -> List[Dict[str, Any]]:
    messages: List[Dict[str, Any]] = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]
    for text in follow_up:
        messages.append({"role": "user", "content": text})
    return messages


def agent_loop(client: OpenAI, options: AgentOptions) -> None:
    """Enhanced agent loop with unrestricted execution and improved UI."""
    messages = build_messages(
        options.system_prompt,
        options.user_prompt,
        options.follow_up,
    )
    specs = tool_schemas()
    thought_console = Console(stderr=True, highlight=False)
    transcript_path = options.transcript_path

    # Create executor with enhanced capabilities
    executor = ToolExecutor(
        root=options.workspace,
        read_only=options.read_only,
        allow_global_access=options.allow_global_access,
        tavily_api_key=options.tavily_api_key,
        execution_mode=options.execution_mode,
        auto_approve=options.auto_approve,
        stream_output=options.stream_output,
    )

    if transcript_path:
        transcript_path.parent.mkdir(parents=True, exist_ok=True)

    def log_to_transcript(message: Dict[str, Any], step_index: int) -> None:
        if not transcript_path:
            return
        entry = {"step": step_index, "message": message}
        with transcript_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(entry, ensure_ascii=False) + "\n")

    if transcript_path:
        for seed in messages:
            log_to_transcript(seed, step_index=0)

    start_time = time.perf_counter()
    live_context = (
        LiveThoughtDisplay(thought_console, start_time, enable_reasoning=options.enable_reasoning)
        if options.verbose else nullcontext(None)
    )

    modifying_tools = {"write_file", "move_path", "apply_patch", "download_file"}
    file_operation_tools = {"list_dir", "read_file", "stat_path", "write_file"}
    current_file_ops: Counter[str] = Counter()

    with live_context as live_display:
        def thought(
            message: str,
            *,
            style: str = "bright_blue",
            with_file_ops: bool = False,
        ) -> None:
            if not options.verbose:
                return
            file_ops_payload: Optional[Mapping[str, int]] = (
                current_file_ops if with_file_ops else None
            )
            if isinstance(live_display, LiveThoughtDisplay):
                live_display.update_thought(message, style=style, file_ops=file_ops_payload)
            else:
                elapsed = time.perf_counter() - start_time
                header = f"[bold bright_blue]▌[/] [{style}]{message}[/{style}]"
                if with_file_ops:
                    ops_markup = _format_file_ops_for_console(current_file_ops)
                    if ops_markup:
                        header += f" [cyan]{ops_markup}[/cyan]"
                footer = f"[dim]Elapsed {elapsed:5.1f}s since start[/]"
                thought_console.print(f"{header}\n{footer}")

        def persist_output(output: str) -> None:
            if not options.verbose:
                return
            if isinstance(live_display, LiveThoughtDisplay):
                live_display.persist(output)
            else:
                thought_console.print(output, markup=False)

        for step in range(1, options.max_steps + 1):
            current_file_ops.clear()
            if options.verbose:
                last_message = messages[-1]
                last_role = last_message.get("role")
                last_length = len(str(last_message.get("content", "")))
                thought(
                    f"Step {step}: requesting model reasoning…\n"
                    f"[dim]Last message {last_role} · {last_length} characters[/]",
                    with_file_ops=True,
                )
            response = client.chat.completions.create(
                model=options.model,
                messages=messages,
                tools=specs,
                tool_choice="auto",
            )
            message = response.choices[0].message
            reasoning_payload = getattr(message, "reasoning_content", None)
            content_chunks = (
                _extract_text_chunks(message.content)
                if message.content is not None
                else []
            )
            content_text = "\n".join(chunk.strip() for chunk in content_chunks if chunk).strip()
            if options.verbose and isinstance(live_display, LiveThoughtDisplay):
                if reasoning_payload:
                    for chunk in _extract_text_chunks(reasoning_payload):
                        snippet = chunk.strip()
                        if snippet:
                            live_display.show_reasoning(snippet)
                plan_lines = _extract_plan_lines(content_text)
                if plan_lines:
                    live_display.show_plan(plan_lines)
            if message.tool_calls:
                tool_payload = [
                    {
                        "id": tc.id,
                        "type": tc.type,
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments,
                        },
                    }
                    for tc in message.tool_calls
                ]
                assistant_tool_message = {
                    "role": "assistant",
                    "content": message.content or "",
                    "tool_calls": tool_payload,
                }
                messages.append(assistant_tool_message)
                log_to_transcript(assistant_tool_message, step_index=step)
                for tool_call in message.tool_calls:
                    name = tool_call.function.name
                    try:
                        arguments = json.loads(tool_call.function.arguments or "{}")
                    except json.JSONDecodeError as exc:
                        result = f"Failed to decode arguments for {name}: {exc}"
                    else:
                        # Show enhanced tool execution display
                        if options.verbose and isinstance(live_display, LiveThoughtDisplay):
                            live_display.show_tool_execution(name, arguments)

                        # Execute tool with no permission checks in unrestricted mode
                        try:
                            result = execute_tool(executor, name, arguments)
                        except Exception as exc:  # pragma: no cover
                            result = f"Tool '{name}' raised an error: {exc}"
                    if name in file_operation_tools:
                        current_file_ops[name] += 1
                        if options.verbose and isinstance(live_display, LiveThoughtDisplay):
                            live_display.update_file_ops(current_file_ops)
                    if isinstance(result, str) and len(result) > MAX_TOOL_RESULT_CHARS:
                        original_len = len(result)
                        result = (
                            result[:MAX_TOOL_RESULT_CHARS]
                            + "\n… output truncated to "
                            + str(MAX_TOOL_RESULT_CHARS)
                            + f" characters (original length {original_len})."
                        )
                    tool_message = {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": result,
                    }
                    messages.append(tool_message)
                    log_to_transcript(tool_message, step_index=step)
                    if name in modifying_tools and isinstance(result, str):
                        persist_output(result)
                    elif name == "run_shell" and isinstance(result, str):
                        thought(
                            f"{name} completed · {len(result)} characters captured.",
                            style="dim",
                        )
            else:
                content = message.content or ""
                assistant_message = {"role": "assistant", "content": content}
                messages.append(assistant_message)
                log_to_transcript(assistant_message, step_index=step)
                if options.verbose and isinstance(live_display, LiveThoughtDisplay):
                    live_display.clear()
                print(content)
                thought("Assistant produced final answer; ending loop.", style="green")
                return
    if transcript_path:
        try:
            location_str = str(transcript_path.relative_to(options.workspace))
        except ValueError:
            location_str = str(transcript_path)
        message = (
            "Max steps reached without a final response. "
            f"Transcript saved to '{location_str}'."
        )
    else:
        message = (
            "Max steps reached without a final response. "
            "Re-run with a higher --max-steps or provide --transcript to inspect the conversation."
        )
    print(message, file=sys.stderr)
    thought("Reached maximum steps without completion.", style="red")


__all__ = [
    "AgentOptions",
    "ToolExecutor",
    "tool_schemas",
    "agent_loop",
]
