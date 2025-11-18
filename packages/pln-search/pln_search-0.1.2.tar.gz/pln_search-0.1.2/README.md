# pln-search

[![Tests](https://github.com/dannyob/pln-search/workflows/Test/badge.svg)](https://github.com/dannyob/pln-search/actions)

Command-line tool for searching the Protocol Labs Network Directory API.

## Installation

### From PyPI (recommended)

```bash
pip install pln-search
```

### From source

```bash
git clone https://github.com/dannyob/pln-search.git
cd pln-search
pip install -e .
```

## Usage

### Authentication

The PLN Directory uses Privy for web authentication. Until we implement a full OAuth2 flow for CLI tools, you'll need to manually configure your authentication token:

**Step 1: Get your token from the browser**

1. Visit https://directory.plnetwork.io/ and log in
2. Open browser Developer Tools (F12 or right-click → Inspect)
3. Go to the **Application** tab (Chrome) or **Storage** tab (Firefox)
4. In the left sidebar, expand **Cookies** and select: `https://directory.plnetwork.io`
5. Find the **`authToken`** cookie and copy its VALUE (a long string starting with `eyJ...`)
6. Optional: Also copy the **`refreshToken`** cookie value

**Step 2: Configure the token**

Option A - Interactive (recommended):
```bash
pln-search auth token --interactive
```

Option B - Command line:
```bash
pln-search auth token YOUR_TOKEN_HERE
```

**Check authentication status:**
```bash
pln-search auth status
```

**Logout (clear credentials):**
```bash
pln-search auth logout
```

### Searching

Search:
```bash
pln-search search "John Doe"                 # Global search
pln-search search --members "John Doe"       # Search members
pln-search search --teams "Protocol Labs"    # Search teams
pln-search search --projects "IPFS"          # Search projects
```

Options:
```bash
pln-search search "query" --limit 50         # Show up to 50 results
pln-search search "query" --json             # JSON output
pln-search search "query" --no-color         # Plain text output
```

## Development

Install dependencies:
```bash
make install-dev
```

Run tests:
```bash
make test
```

Format code:
```bash
make format
```

## Development Status

**Implemented:**
- ✓ Data models (Member, Team, Project)
- ✓ Configuration management with XDG directories
- ✓ API client with search methods
- ✓ Output formatters (rich, plain, JSON)
- ✓ OAuth2 token refresh
- ✓ CLI commands
- ✓ Test suite

**TODO for production use:**
- [ ] Full OAuth2 browser flow (currently stub)
- [ ] Integration testing with real API
- [ ] Error message improvements
- [ ] Performance optimization
- [ ] PyPI packaging

## Testing

The project includes a comprehensive test suite. Note that OAuth2 browser authentication is currently a stub and requires manual token setup for testing against the real API.

For local development and testing, mock the API responses.
