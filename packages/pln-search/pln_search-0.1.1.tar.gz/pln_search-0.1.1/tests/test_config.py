"""Tests for configuration management."""

import json
from pathlib import Path
from pln_search.config import ConfigManager


def test_get_config_dir(tmp_path, monkeypatch):
    """Test config directory is created."""
    # Mock platformdirs to use temp directory
    monkeypatch.setenv("HOME", str(tmp_path))

    config = ConfigManager()
    config_dir = config.get_config_dir()

    assert config_dir.exists()
    assert config_dir.is_dir()


def test_save_and_load_credentials(tmp_path, monkeypatch):
    """Test saving and loading credentials."""
    monkeypatch.setenv("HOME", str(tmp_path))

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
    monkeypatch.setenv("HOME", str(tmp_path))

    config = ConfigManager()
    loaded = config.load_credentials()

    assert loaded is None


def test_clear_credentials(tmp_path, monkeypatch):
    """Test clearing credentials."""
    monkeypatch.setenv("HOME", str(tmp_path))

    config = ConfigManager()
    config.save_credentials({"refresh_token": "test"})

    assert config.load_credentials() is not None

    config.clear_credentials()

    assert config.load_credentials() is None
