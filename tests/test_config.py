import pytest
from support_agent.config import get_api_key

def test_returns_key_when_set(monkeypatch):
    monkeypatch.setenv("LLM_API_KEY", "test_key")
    assert get_api_key() == "test_key"

def test_missing_key_raises_clear_error(monkeypatch):
    monkeypatch.delenv("LLM_API_KEY", raising=False)
    with pytest.raises(RuntimeError):
        get_api_key()