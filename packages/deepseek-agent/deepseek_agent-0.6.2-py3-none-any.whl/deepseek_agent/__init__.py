"""Public helpers for configuring DeepSeek Agent credentials."""

from __future__ import annotations

from typing import Optional

try:  # pragma: no cover - optional dependency
    from dotenv import load_dotenv
except Exception:  # pragma: no cover - fallback when dotenv is missing
    def load_dotenv(*_args, **_kwargs) -> bool:
        return False
else:  # pragma: no cover - trivial invocation
    load_dotenv()

from deepseek_cli import __version__ as __version__
from deepseek_cli.constants import DEFAULT_TAVILY_API_KEY
from deepseek_cli.keys import (
    ENV_API_KEY,
    ENV_TAVILY_API_KEY,
    configure_api_keys as _configure_api_keys,
    get_deepseek_api_key as _get_deepseek_api_key,
    get_tavily_api_key as _get_tavily_api_key,
    set_deepseek_api_key as _set_deepseek_api_key,
    set_tavily_api_key as _set_tavily_api_key,
)

DEEPSEEK_API_KEY: Optional[str] = None
TAVILY_API_KEY: Optional[str] = None


def _refresh_module_state() -> None:
    global DEEPSEEK_API_KEY, TAVILY_API_KEY
    DEEPSEEK_API_KEY = _get_deepseek_api_key()
    TAVILY_API_KEY = _get_tavily_api_key(DEFAULT_TAVILY_API_KEY)


def get_deepseek_api_key() -> Optional[str]:
    """Return the active DeepSeek API key."""

    _refresh_module_state()
    return DEEPSEEK_API_KEY


def set_deepseek_api_key(value: Optional[str], *, update_env: bool = True) -> None:
    """Override the DeepSeek API key without requiring environment exports."""

    _set_deepseek_api_key(value, update_env=update_env)
    _refresh_module_state()


def get_tavily_api_key() -> Optional[str]:
    """Return the active Tavily API key (falls back to the bundled developer key)."""

    _refresh_module_state()
    return TAVILY_API_KEY


def set_tavily_api_key(value: Optional[str], *, update_env: bool = True) -> None:
    """Override the Tavily API key without requiring environment exports."""

    _set_tavily_api_key(value, update_env=update_env)
    _refresh_module_state()


def configure_api_keys(
    *,
    deepseek_api_key: Optional[str] = None,
    tavily_api_key: Optional[str] = None,
    update_env: bool = True,
) -> None:
    """Convenience helper to set one or both API keys."""

    _configure_api_keys(
        deepseek_api_key=deepseek_api_key,
        tavily_api_key=tavily_api_key,
        update_env=update_env,
    )
    _refresh_module_state()


_refresh_module_state()

__all__ = [
    "DEEPSEEK_API_KEY",
    "TAVILY_API_KEY",
    "ENV_API_KEY",
    "ENV_TAVILY_API_KEY",
    "DEFAULT_TAVILY_API_KEY",
    "configure_api_keys",
    "get_deepseek_api_key",
    "get_tavily_api_key",
    "set_deepseek_api_key",
    "set_tavily_api_key",
    "__version__",
]
