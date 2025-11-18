"""Configuration management for pln-search."""

import json
from pathlib import Path
from platformdirs import user_config_dir


class ConfigManager:
    """Manage configuration and credentials for pln-search."""

    def __init__(self):
        """Initialize config manager."""
        self.app_name = "pln-search"
        self.app_author = "pln"

    def get_config_dir(self) -> Path:
        """Get platform-specific config directory.

        Returns:
            Path to config directory (creates if doesn't exist)
        """
        config_dir = Path(user_config_dir(self.app_name, self.app_author))
        config_dir.mkdir(parents=True, exist_ok=True)
        return config_dir

    def _get_credentials_file(self) -> Path:
        """Get path to credentials file."""
        return self.get_config_dir() / "credentials.json"

    def save_credentials(self, credentials: dict) -> None:
        """Save credentials to file with restricted permissions.

        Args:
            credentials: Dict containing tokens and user info
        """
        creds_file = self._get_credentials_file()

        # Write credentials
        with open(creds_file, "w") as f:
            json.dump(credentials, f, indent=2)

        # Set restrictive permissions (0600)
        creds_file.chmod(0o600)

    def load_credentials(self) -> dict | None:
        """Load credentials from file.

        Returns:
            Credentials dict or None if file doesn't exist
        """
        creds_file = self._get_credentials_file()

        if not creds_file.exists():
            return None

        with open(creds_file) as f:
            return json.load(f)

    def clear_credentials(self) -> None:
        """Delete credentials file (logout)."""
        creds_file = self._get_credentials_file()

        if creds_file.exists():
            creds_file.unlink()

    def get_api_base_url(self) -> str:
        """Get API base URL from environment or default.

        Returns:
            API base URL
        """
        import os
        return os.environ.get("PLN_API_URL", "https://api-directory.plnetwork.io")
