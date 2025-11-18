"""OAuth2 authentication flow."""

import requests
from datetime import datetime
from pln_search.config import ConfigManager


class AuthenticationError(Exception):
    """Authentication failed."""
    pass


class OAuth2Flow:
    """Handle OAuth2 authentication flow."""

    def __init__(self, api_base_url: str, config: ConfigManager):
        """Initialize OAuth2 flow.

        Args:
            api_base_url: Base URL for API
            config: Configuration manager
        """
        self.api_base_url = api_base_url.rstrip("/")
        self.config = config

    def get_valid_token(self) -> str:
        """Get a valid access token, refreshing if needed.

        Returns:
            Valid access token

        Raises:
            AuthenticationError: If not authenticated or refresh fails
        """
        creds = self.config.load_credentials()

        if not creds:
            raise AuthenticationError(
                "Not authenticated. Run: pln-search auth"
            )

        # Check if token is expired
        expires_at = datetime.fromisoformat(creds["expires_at"])
        now = datetime.now()

        # Refresh if expired or expiring soon (< 5 minutes)
        if expires_at <= now or (expires_at - now).total_seconds() < 300:
            return self._refresh_token(creds["refresh_token"])

        return creds["access_token"]

    def _refresh_token(self, refresh_token: str) -> str:
        """Refresh access token using refresh token.

        Args:
            refresh_token: Refresh token

        Returns:
            New access token

        Raises:
            AuthenticationError: If refresh fails
        """
        url = f"{self.api_base_url}/v1/auth/token"

        try:
            response = requests.post(
                url,
                json={
                    "grantType": "refresh_token",
                    "refreshToken": refresh_token,
                },
                timeout=30,
            )

            response.raise_for_status()
            data = response.json()

            # Update stored credentials
            self.config.save_credentials({
                "access_token": data["accessToken"],
                "refresh_token": data["refreshToken"],
                "expires_at": datetime.now().isoformat(),  # TODO: Calculate from expires_in
                "user_info": data.get("userInfo", {}),
            })

            return data["accessToken"]

        except requests.exceptions.RequestException as e:
            raise AuthenticationError(f"Token refresh failed: {e}")

    def set_manual_credentials(self, access_token: str, refresh_token: str = None) -> None:
        """Manually set credentials from token.

        Args:
            access_token: Access token from PLN API
            refresh_token: Optional refresh token
        """
        # For now, set a far future expiration (1 year)
        # In reality, tokens expire much sooner, but refresh_token will handle it
        from datetime import timedelta
        expires_at = (datetime.now() + timedelta(days=365)).isoformat()

        credentials = {
            "access_token": access_token,
            "refresh_token": refresh_token or access_token,
            "expires_at": expires_at,
            "user_info": {},
        }

        self.config.save_credentials(credentials)

    def start_auth_flow(self) -> None:
        """Start OAuth2 browser authentication flow.

        For now, this provides instructions for manual token setup.
        Full OAuth2 browser flow is not yet implemented.
        """
        print("=" * 70)
        print("MANUAL TOKEN SETUP")
        print("=" * 70)
        print()
        print("The PLN Directory uses Privy for web authentication, which is not")
        print("suitable for CLI tools. Until we implement a proper OAuth2 flow,")
        print("please set up authentication manually by extracting tokens from")
        print("browser cookies:")
        print()
        print("1. Visit https://directory.plnetwork.io/ and log in")
        print()
        print("2. Open browser Developer Tools (F12 or right-click → Inspect)")
        print()
        print("3. Go to the 'Application' tab (Chrome) or 'Storage' tab (Firefox)")
        print()
        print("4. In the left sidebar, expand 'Cookies' and select:")
        print("   https://directory.plnetwork.io")
        print()
        print("5. Find the 'authToken' cookie and copy its VALUE")
        print("   (It's a long string starting with 'eyJ...')")
        print()
        print("6. Optional: Also copy the 'refreshToken' cookie value")
        print()
        print("7. Run: pln-search auth token --interactive")
        print()
        print("8. Paste the authToken when prompted")
        print()
        print("=" * 70)
        print()
        print("Quick method: pln-search auth token <your-authToken-value>")
        print()
        print("With refresh token: pln-search auth token <authToken>")
        print("                    --refresh-token <refreshToken>")
        print("=" * 70)
