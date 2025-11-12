"""Runtime helpers for DeepSeek and Tavily API keys."""

from __future__ import annotations

import os
from typing import Optional

ENV_API_KEY = "DEEPSEEK_API_KEY"
ENV_TAVILY_API_KEY = "TAVILY_API_KEY"

_deepseek_api_key_override: Optional[str] = None
_tavily_api_key_override: Optional[str] = None


def _normalize(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    stripped = value.strip()
    return stripped or None


def get_deepseek_api_key(default: Optional[str] = None) -> Optional[str]:
    """Return the DeepSeek API key override, environment value, or default."""

    return _deepseek_api_key_override or os.environ.get(ENV_API_KEY) or default


def set_deepseek_api_key(value: Optional[str], *, update_env: bool = False) -> None:
    """Override the DeepSeek API key for the current process."""

    global _deepseek_api_key_override
    normalized = _normalize(value)
    _deepseek_api_key_override = normalized
    if update_env:
        if normalized is None:
            os.environ.pop(ENV_API_KEY, None)
        else:
            os.environ[ENV_API_KEY] = normalized


def get_tavily_api_key(default: Optional[str] = None) -> Optional[str]:
    """Return the Tavily API key override, environment value, or default."""

    return _tavily_api_key_override or os.environ.get(ENV_TAVILY_API_KEY) or default


def set_tavily_api_key(value: Optional[str], *, update_env: bool = False) -> None:
    """Override the Tavily API key for the current process."""

    global _tavily_api_key_override
    normalized = _normalize(value)
    _tavily_api_key_override = normalized
    if update_env:
        if normalized is None:
            os.environ.pop(ENV_TAVILY_API_KEY, None)
        else:
            os.environ[ENV_TAVILY_API_KEY] = normalized


def configure_api_keys(
    *,
    deepseek_api_key: Optional[str] = None,
    tavily_api_key: Optional[str] = None,
    update_env: bool = False,
) -> None:
    """Convenience helper to configure one or both API keys."""

    if deepseek_api_key is not None:
        set_deepseek_api_key(deepseek_api_key, update_env=update_env)
    if tavily_api_key is not None:
        set_tavily_api_key(tavily_api_key, update_env=update_env)


__all__ = [
    "ENV_API_KEY",
    "ENV_TAVILY_API_KEY",
    "configure_api_keys",
    "get_deepseek_api_key",
    "get_tavily_api_key",
    "set_deepseek_api_key",
    "set_tavily_api_key",
]
