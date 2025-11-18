"""Tests for authentication."""

from datetime import datetime, timedelta
from unittest.mock import Mock, patch
from pln_search.auth import OAuth2Flow
from pln_search.config import ConfigManager


def test_get_valid_token_fresh(tmp_path, monkeypatch):
    """Test getting token when it's still valid."""
    monkeypatch.setenv("HOME", str(tmp_path))

    config = ConfigManager()
    config.save_credentials({
        "access_token": "fresh_token",
        "refresh_token": "refresh",
        "expires_at": (datetime.now() + timedelta(hours=1)).isoformat(),
    })

    auth = OAuth2Flow("https://api.test.com", config)
    token = auth.get_valid_token()

    assert token == "fresh_token"


def test_get_valid_token_missing(tmp_path, monkeypatch):
    """Test getting token when credentials missing."""
    monkeypatch.setenv("HOME", str(tmp_path))

    config = ConfigManager()
    auth = OAuth2Flow("https://api.test.com", config)

    try:
        auth.get_valid_token()
        assert False, "Should raise exception"
    except Exception as e:
        assert "not authenticated" in str(e).lower()
