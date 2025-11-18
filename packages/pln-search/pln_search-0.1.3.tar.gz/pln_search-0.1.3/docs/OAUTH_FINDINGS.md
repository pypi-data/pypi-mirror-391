# OAuth2 Authentication Investigation Findings

## Summary

The PLN Directory uses **Privy** (https://privy.io) as their authentication provider for the web interface. Authentication tokens are stored in **browser cookies**, not Authorization headers. This creates some complexity for implementing CLI authentication.

## Key Discovery: Cookie-Based Authentication

The web application stores authentication in **cookies**:
- **`authToken`** - JWT access token (starts with `eyJ...`)
- **`refreshToken`** - JWT refresh token
- **`userInfo`** - JSON with user details (name, email, uid, accessLevel, etc.)

The API expects these tokens to be sent as `Authorization: Bearer <token>` headers, so the frontend extracts them from cookies and sends them in requests.

## What I Found

### Frontend (Web)
- The directory website at https://directory.plnetwork.io/ uses Privy for authentication
- Login modal offers multiple methods:
  - Continue with Email
  - Google OAuth
  - GitHub OAuth
  - Wallet (likely MetaMask/Web3)

### Privy Integration
When clicking "Sign in with Google", the flow is:
1. User clicks button
2. Browser redirects to Google OAuth: `https://accounts.google.com/o/oauth2/v2/auth`
3. Redirect URI points to Privy: `https://auth.privy.io/api/v1/oauth/callback`
4. Privy handles the OAuth callback and token exchange
5. Privy likely provides a token that the frontend uses with the PLN API

### PLN API (Backend)
According to `API.md`, the PLN API has its own OAuth2 endpoints:

**POST /v1/auth** - Creates auth request
```json
Request: {"state": "random_state_string"}
Response: "uid_of_auth_request"
```

**POST /v1/auth/token** - Exchange code for tokens
```json
Request: {"grantType": "authorization_code", "code": "auth_code"}
Response: {"accessToken": "...", "refreshToken": "...", "userInfo": {...}}
```

## The Challenge for CLI

The web interface uses Privy (third-party service), but the CLI needs to authenticate directly with the PLN API. The disconnect is:

1. **Web flow**: User → Privy → Google/GitHub → Privy → PLN API
2. **CLI needs**: User → PLN API (direct)

We don't know the full authorization URL or flow for the PLN API's OAuth endpoints because the frontend delegates everything to Privy.

## Recommended Solutions

### Short-term (Current Implementation)
The stub in `src/pln_search/auth.py` is appropriate for now:
```python
def start_auth_flow(self) -> None:
    print("OAuth2 browser flow not yet implemented.")
    print("Manual token entry:")
    print("1. Obtain access token from PLN API")
    print("2. Save to credentials manually")
    raise NotImplementedError("Full OAuth2 flow coming soon")
```

**Workaround for testing:**
1. User logs in via web browser at https://directory.plnetwork.io/
2. User opens browser dev tools → Application/Storage tab → Cookies
3. Find the `authToken` cookie and copy its value (JWT starting with `eyJ...`)
4. Optionally copy the `refreshToken` cookie value
5. Use the CLI command: `pln-search auth token --interactive`
6. Paste the tokens when prompted

Alternatively, manually save to `~/.config/pln-search/credentials.json`:
```json
{
  "access_token": "eyJhbGc...",
  "refresh_token": "eyJhbGc...",
  "expires_at": "2025-11-13T00:00:00",
  "user_info": {
    "name": "User Name",
    "email": "user@example.com"
  }
}
```

### Long-term Options

#### Option 1: Browser Flow with Localhost Callback
Implement a standard OAuth2 browser flow:
1. CLI starts local HTTP server on `http://localhost:8080`
2. CLI opens browser to PLN auth URL (need to discover this)
3. User authenticates in browser
4. Browser redirects to `http://localhost:8080/callback?code=...`
5. CLI exchanges authorization code for tokens

**Requires**: Understanding the full PLN API OAuth flow (authorization URL, required parameters)

#### Option 2: Device Flow
Similar to GitHub CLI's `gh auth login`:
1. CLI generates a device code
2. User visits a URL and enters the code
3. CLI polls API for token

**Requires**: PLN API supporting device flow (RFC 8628)

#### Option 3: API Key / Service Account
If PLN offers API keys for programmatic access:
1. User generates API key from web interface
2. User saves API key to CLI config
3. CLI uses API key for authentication

**Requires**: PLN API supporting API keys

## Next Steps

1. **Contact PLN API team** to ask about:
   - How should CLI tools authenticate?
   - Is there a device flow or API key system?
   - What is the full OAuth2 authorization URL?
   - Can we get OAuth2 client credentials for a CLI application?

2. **For now, use manual token entry** as documented in README

3. **Once we have clarity**, implement the appropriate auth flow

## Files to Update (Future)

When implementing full OAuth2:
- `src/pln_search/auth.py` - Replace stub with actual browser flow
- `src/pln_search/cli.py` - Update `auth login` command
- `tests/test_auth.py` - Add integration tests
- `README.md` - Update authentication documentation
