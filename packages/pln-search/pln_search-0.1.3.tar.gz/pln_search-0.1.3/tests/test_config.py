"""Tests for configuration management."""

import json
from pathlib import Path
from pln_search.config import ConfigManager


def test_get_config_dir(tmp_path, monkeypatch):
    """Test config directory is created."""
    # Mock platformdirs to use temp directory
    def mock_user_config_dir(app_name, app_author):
        return str(tmp_path / ".config" / app_name)

    monkeypatch.setattr("pln_search.config.user_config_dir", mock_user_config_dir)

    config = ConfigManager()
    config_dir = config.get_config_dir()

    assert config_dir.exists()
    assert config_dir.is_dir()


def test_save_and_load_credentials(tmp_path, monkeypatch):
    """Test saving and loading credentials."""
    # Mock platformdirs to use temp directory
    def mock_user_config_dir(app_name, app_author):
        return str(tmp_path / ".config" / app_name)

    monkeypatch.setattr("pln_search.config.user_config_dir", mock_user_config_dir)

    config = ConfigManager()

    test_creds = {
        "refresh_token": "test_refresh",
        "access_token": "test_access",
        "expires_at": "2025-11-12T10:00:00Z",
        "user_info": {"uid": "u123", "email": "test@example.com"},
    }

    config.save_credentials(test_creds)
    loaded = config.load_credentials()

    assert loaded == test_creds
    assert loaded["refresh_token"] == "test_refresh"


def test_load_credentials_missing(tmp_path, monkeypatch):
    """Test loading credentials when file doesn't exist."""
    # Mock platformdirs to use temp directory
    def mock_user_config_dir(app_name, app_author):
        return str(tmp_path / ".config" / app_name)

    monkeypatch.setattr("pln_search.config.user_config_dir", mock_user_config_dir)

    config = ConfigManager()
    loaded = config.load_credentials()

    assert loaded is None


def test_clear_credentials(tmp_path, monkeypatch):
    """Test clearing credentials."""
    # Mock platformdirs to use temp directory
    def mock_user_config_dir(app_name, app_author):
        return str(tmp_path / ".config" / app_name)

    monkeypatch.setattr("pln_search.config.user_config_dir", mock_user_config_dir)

    config = ConfigManager()
    config.save_credentials({"refresh_token": "test"})

    assert config.load_credentials() is not None

    config.clear_credentials()

    assert config.load_credentials() is None
