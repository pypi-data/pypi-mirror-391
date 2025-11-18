# PLN Search CLI Tool - Design Document

**Date:** 2025-11-11
**Author:** Danny O'Brien
**Repository:** ~/Public/src/dob/pln-search

## Purpose

The `pln-search` tool provides command-line access to the PLN Directory API. Users can search for members, teams, and projects directly from their terminal.

## Requirements

### Functional Requirements

1. **Authentication**: OAuth2 flow via browser with token refresh
2. **Search**: Query members, teams, and projects by name/keyword
3. **Output**: Rich tables for terminals, plain text for pipes, JSON on demand
4. **Storage**: Store credentials in platform-specific config directories

### Non-Functional Requirements

1. **Performance**: Fast startup (<500ms), efficient API calls
2. **Usability**: Intuitive CLI, clear error messages
3. **Portability**: Works on Linux, macOS, Windows
4. **Security**: Credentials stored with restrictive permissions (0600)

## Architecture

### Package Structure

```
pln-search/
├── pyproject.toml           # uv package definition
├── README.md                # Usage documentation
├── Makefile                 # Development tasks
├── .gitignore
├── pln_search/              # Main package
│   ├── __init__.py         # Version info
│   ├── __main__.py         # Entry point (python -m pln_search)
│   ├── cli.py              # Click commands
│   ├── api.py              # PLNAPIClient class
│   ├── auth.py             # OAuth2Flow class
│   ├── config.py           # ConfigManager class
│   ├── formatters.py       # OutputFormatter class
│   └── models.py           # Dataclasses (Member, Team, Project)
└── tests/
    └── __init__.py
```

### Component Design

#### cli.py - Command Interface

**Commands:**
```bash
pln-search auth              # Start OAuth2 login
pln-search auth --status     # Check authentication
pln-search auth --logout     # Remove credentials

pln-search [query]           # Global search
pln-search --members [query] # Search members only
pln-search --teams [query]   # Search teams only
pln-search --projects [query] # Search projects only

# Options
--limit N                    # Show N results (default: 20)
--json                       # Output JSON
--no-color                   # Plain text output
```

**Responsibilities:**
- Parse command-line arguments with Click
- Load configuration and validate authentication
- Call API client methods
- Pass results to formatter
- Handle errors with clear messages

#### auth.py - OAuth2 Authentication

**OAuth2Flow Class:**

```python
class OAuth2Flow:
    def start_auth() -> None
        # 1. POST /v1/auth → get requestUid
        # 2. Open browser to OAuth consent page
        # 3. Start localhost:8765 server for callback
        # 4. Receive code, exchange for tokens
        # 5. Save credentials

    def get_valid_token() -> str
        # Check expiration, refresh if needed
        # Return valid access token

    def _refresh_token(refresh_token: str) -> TokenResponse
        # POST /v1/auth/token with grantType: refresh_token
```

**Flow:**
1. User runs `pln-search auth`
2. Tool creates auth request at API
3. Browser opens to OAuth consent page
4. User authorizes, redirects to localhost
5. Tool exchanges code for tokens
6. Tool saves refresh token securely

#### config.py - Configuration Management

**ConfigManager Class:**

```python
class ConfigManager:
    def get_config_dir() -> Path
        # Linux: ~/.config/pln-search/
        # macOS: ~/Library/Application Support/pln-search/
        # Windows: %APPDATA%/pln-search/
        # Uses platformdirs library

    def save_credentials(tokens: TokenResponse) -> None
        # Write to credentials.json with 0600 permissions

    def load_credentials() -> dict | None
        # Return credentials or None if missing

    def clear_credentials() -> None
        # Delete credentials.json (logout)
```

**Credentials Format:**
```json
{
  "refresh_token": "eyJhbGc...",
  "access_token": "eyJhbGc...",
  "expires_at": "2025-11-12T10:30:00Z",
  "user_info": {
    "uid": "member_uid",
    "email": "user@example.com",
    "name": "User Name"
  }
}
```

#### api.py - API Client

**PLNAPIClient Class:**

```python
class PLNAPIClient:
    def __init__(base_url: str, auth: OAuth2Flow)

    def search_members(query: str, limit: int) -> list[Member]
        # GET /v1/members/search?q={query}&limit={limit}

    def search_teams(query: str, limit: int) -> list[Team]
        # GET /v1/teams?name__icontains={query}&limit={limit}

    def search_projects(query: str, limit: int) -> list[Project]
        # GET /v1/projects?name__icontains={query}&limit={limit}

    def global_search(query: str) -> SearchResults
        # GET /v1/search?q={query}
        # Returns combined results from all types
```

**Error Handling:**
- Network errors → "Cannot reach PLN API. Check connection."
- 401 Unauthorized → "Authentication expired. Run: pln-search auth"
- 403 Forbidden → "Access denied. Check permissions."
- 404 Not Found → "No results found."
- 500 Server Error → "API error. Try again later."

#### models.py - Data Structures

**Dataclasses:**

```python
@dataclass
class Member:
    uid: str
    name: str
    email: str | None
    bio: str | None
    location: str | None
    skills: list[str]
    github_handler: str | None

@dataclass
class Team:
    uid: str
    name: str
    short_description: str | None
    website: str | None
    member_count: int

@dataclass
class Project:
    uid: str
    name: str
    description: str | None
    maintaining_team: str | None
    looking_for_funding: bool
```

#### formatters.py - Output Formatting

**OutputFormatter Class:**

```python
class OutputFormatter:
    def __init__(format_type: Literal["auto", "rich", "plain", "json"])

    def format_members(members: list[Member]) -> None
    def format_teams(teams: list[Team]) -> None
    def format_projects(projects: list[Project]) -> None
```

**Format Types:**

1. **Rich (terminal)**:
   - Colored tables with borders
   - Truncates long text to fit terminal width
   - Shows column headers
   - Example: Name | Location | Skills | GitHub

2. **Plain (pipes)**:
   - Simple text output, one result per line
   - Format: "Name (location) - skill1, skill2"
   - No colors, no table borders

3. **JSON**:
   - Full JSON array of results
   - All fields included
   - Machine-readable for piping to jq

**Auto-detection:**
```python
if sys.stdout.isatty():
    use_rich_format()
else:
    use_plain_format()
```

## Dependencies

```toml
[project]
dependencies = [
    "click>=8.1.0",        # CLI framework
    "requests>=2.31.0",    # HTTP client
    "rich>=13.0.0",        # Terminal formatting
    "platformdirs>=4.0.0", # XDG directories
]
```

**Rationale:**
- **click**: Industry standard for CLIs, clean API
- **requests**: Simple, reliable HTTP
- **rich**: Beautiful terminal output with auto-detection
- **platformdirs**: Cross-platform config paths

## Development Setup

**Using uv:**
```bash
cd ~/Public/src/dob/pln-search
uv init --package pln-search
uv add click requests rich platformdirs
```

**Makefile targets:**
```make
make install      # Install package (editable)
make install-dev  # Install with dev dependencies
make test         # Run tests
make lint         # Run ruff
make format       # Format code
make check        # Lint + test
make build        # Build distribution
make clean        # Remove artifacts
```

## Security Considerations

1. **Credential Storage**:
   - File permissions: 0600 (owner read/write only)
   - Never log tokens to stdout/stderr
   - Clear tokens on logout

2. **OAuth2 Flow**:
   - Use state parameter to prevent CSRF
   - Localhost callback server binds to 127.0.0.1 only
   - Server shuts down after receiving callback

3. **API Communication**:
   - HTTPS only (enforce via requests)
   - Validate SSL certificates
   - Timeout requests (30s default)

## Error Handling

**Exit Codes:**
- 0: Success
- 1: General error (network, API, etc.)
- 2: Authentication error
- 3: Invalid arguments

**Error Messages:**
```
✗ Authentication required. Run: pln-search auth
✗ No results found for "query"
✗ Cannot reach PLN API. Check connection.
✗ API error (500). Try again later.
```

## Future Enhancements

**Not in v1, but considered:**
1. Detail view: `pln-search show member <uid>`
2. Interactive selection with arrow keys
3. Caching results locally (configurable TTL)
4. Pagination for large result sets
5. Advanced filters: `--skills rust,go --location "San Francisco"`
6. Configuration file for API URL overrides

## Testing Strategy

**Unit Tests:**
- Mock API responses
- Test OAuth flow (mocked)
- Test formatters with sample data
- Test config manager (temp directories)

**Integration Tests:**
- Test against mock API server
- Verify end-to-end auth flow
- Check output format detection

**Manual Testing:**
- Test on Linux, macOS, Windows
- Verify XDG directory usage
- Test with real PLN API (staging)

## Installation

**From source:**
```bash
git clone ~/Public/src/dob/pln-search
cd pln-search
uv pip install -e .
```

**After development:**
```bash
uv build
uv pip install dist/pln_search-0.1.0-py3-none-any.whl
```

**Entry point:**
- Installed command: `pln-search`
- Module invocation: `python -m pln_search`

## Configuration

**API Base URL:**
- Default: From environment variable `PLN_API_URL`
- Fallback: Hardcoded in code
- Future: Support config file override

**Example:**
```bash
export PLN_API_URL="https://api.pln.network"
pln-search --members "John Doe"
```

## Open Questions

None. Design is complete and approved.

## References

- API Documentation: [API.md](../../API.md) in this repository
- OAuth2 Endpoints: POST /v1/auth, POST /v1/auth/token
- Search Endpoints: GET /v1/search, GET /v1/members/search
