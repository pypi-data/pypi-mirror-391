"""Tests for authentication."""

from datetime import datetime, timedelta
from unittest.mock import Mock, patch
from pln_search.auth import OAuth2Flow
from pln_search.config import ConfigManager


def test_get_valid_token_fresh(tmp_path, monkeypatch):
    """Test getting token when it's still valid."""
    # Mock platformdirs to use temp directory
    def mock_user_config_dir(app_name, app_author):
        return str(tmp_path / ".config" / app_name)

    monkeypatch.setattr("pln_search.config.user_config_dir", mock_user_config_dir)

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
    # Mock platformdirs to use temp directory
    def mock_user_config_dir(app_name, app_author):
        return str(tmp_path / ".config" / app_name)

    monkeypatch.setattr("pln_search.config.user_config_dir", mock_user_config_dir)

    config = ConfigManager()
    auth = OAuth2Flow("https://api.test.com", config)

    try:
        auth.get_valid_token()
        assert False, "Should raise exception"
    except Exception as e:
        assert "not authenticated" in str(e).lower()
