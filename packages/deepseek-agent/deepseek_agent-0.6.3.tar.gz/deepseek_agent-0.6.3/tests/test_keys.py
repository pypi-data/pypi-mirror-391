from __future__ import annotations

import importlib

from deepseek_cli import keys


def test_get_deepseek_api_key_prefers_override(monkeypatch):
    monkeypatch.delenv(keys.ENV_API_KEY, raising=False)
    keys.set_deepseek_api_key(None)
    assert keys.get_deepseek_api_key() is None

    monkeypatch.setenv(keys.ENV_API_KEY, "ds-env-key")
    assert keys.get_deepseek_api_key() == "ds-env-key"

    keys.set_deepseek_api_key("ds-override")
    assert keys.get_deepseek_api_key() == "ds-override"

    keys.set_deepseek_api_key(None)
    assert keys.get_deepseek_api_key() == "ds-env-key"


def test_get_tavily_api_key_prefers_override(monkeypatch):
    monkeypatch.delenv(keys.ENV_TAVILY_API_KEY, raising=False)
    keys.set_tavily_api_key(None)

    assert keys.get_tavily_api_key() is None

    monkeypatch.setenv(keys.ENV_TAVILY_API_KEY, "tvly-env")
    assert keys.get_tavily_api_key() == "tvly-env"

    keys.set_tavily_api_key("tvly-override")
    assert keys.get_tavily_api_key() == "tvly-override"


def test_configure_api_keys_updates_environment(monkeypatch):
    monkeypatch.delenv(keys.ENV_API_KEY, raising=False)
    monkeypatch.delenv(keys.ENV_TAVILY_API_KEY, raising=False)

    keys.configure_api_keys(
        deepseek_api_key="ds-inline",
        tavily_api_key="tvly-inline",
        update_env=True,
    )

    assert keys.get_deepseek_api_key() == "ds-inline"
    assert keys.get_tavily_api_key() == "tvly-inline"


def test_deepseek_agent_module_reflects_changes(monkeypatch):
    module = importlib.import_module("deepseek_agent")
    monkeypatch.delenv(module.ENV_API_KEY, raising=False)
    monkeypatch.delenv(module.ENV_TAVILY_API_KEY, raising=False)
    keys.set_deepseek_api_key(None)
    keys.set_tavily_api_key(None)

    assert module.get_deepseek_api_key() is None

    module.set_deepseek_api_key("ds-inline")
    module.set_tavily_api_key("tvly-inline")

    assert module.get_deepseek_api_key() == "ds-inline"
    assert module.get_tavily_api_key() == "tvly-inline"
