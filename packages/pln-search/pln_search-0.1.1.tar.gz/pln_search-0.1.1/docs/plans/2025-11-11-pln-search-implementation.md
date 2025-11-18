# PLN Search CLI Tool - Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a command-line tool to search the PLN Directory API for members, teams, and projects.

**Architecture:** Modular Python package using Click for CLI, requests for HTTP, rich for terminal output, and OAuth2 for authentication. Config stored in platform-specific directories.

**Tech Stack:** Python 3.10+, uv (build system), click (CLI), requests (HTTP), rich (formatting), platformdirs (config paths)

---

## Prerequisites

Before starting, ensure:
- Python 3.10+ installed
- uv installed (`curl -LsSf https://astral.sh/uv/install.sh | sh`)
- Access to PLN API documentation (API.md)

---

### Task 1: Repository Setup

**Files:**
- Create: `~/Public/src/dob/pln-search/` (directory)

**Step 1: Create repository directory**

```bash
mkdir -p ~/Public/src/dob/pln-search
cd ~/Public/src/dob/pln-search
```

**Step 2: Initialize uv project**

```bash
uv init --package pln-search
```

Expected: Creates `pyproject.toml`, basic structure

**Step 3: Initialize git repository**

```bash
git init
git add .
git commit -m "chore: initialize pln-search project with uv"
```

---

### Task 2: Configure Project Metadata

**Files:**
- Modify: `~/Public/src/dob/pln-search/pyproject.toml`
- Create: `~/Public/src/dob/pln-search/.gitignore`
- Create: `~/Public/src/dob/pln-search/README.md`

**Step 1: Update pyproject.toml**

Replace contents with:

```toml
[project]
name = "pln-search"
version = "0.1.0"
description = "CLI tool for searching the PLN directory API"
readme = "README.md"
requires-python = ">=3.10"
authors = [
    {name = "Danny O'Brien", email = "danny@spesh.com"}
]
dependencies = [
    "click>=8.1.0",
    "requests>=2.31.0",
    "rich>=13.0.0",
    "platformdirs>=4.0.0",
]

[project.scripts]
pln-search = "pln_search.cli:main"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.ruff]
line-length = 100
target-version = "py310"

[tool.ruff.lint]
select = ["E", "F", "W", "I"]
```

**Step 2: Create .gitignore**

```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
.venv/
venv/
ENV/
env/

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~

# Testing
.pytest_cache/
.coverage
htmlcov/

# OS
.DS_Store
Thumbs.db
```

**Step 3: Create README.md**

```markdown
# pln-search

Command-line tool for searching the PLN Directory API.

## Installation

```bash
uv pip install -e .
```

## Usage

Authenticate:
```bash
pln-search auth
```

Search:
```bash
pln-search "John Doe"                 # Global search
pln-search --members "John Doe"       # Search members
pln-search --teams "Protocol Labs"    # Search teams
pln-search --projects "IPFS"          # Search projects
```

Options:
```bash
pln-search "query" --limit 50         # Show up to 50 results
pln-search "query" --json             # JSON output
pln-search "query" --no-color         # Plain text output
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
```

**Step 4: Commit configuration**

```bash
git add pyproject.toml .gitignore README.md
git commit -m "chore: configure project metadata and documentation"
```

---

### Task 3: Create Package Structure

**Files:**
- Create: `~/Public/src/dob/pln-search/pln_search/__init__.py`
- Create: `~/Public/src/dob/pln-search/pln_search/__main__.py`
- Create: `~/Public/src/dob/pln-search/tests/__init__.py`

**Step 1: Create package init**

File: `pln_search/__init__.py`
```python
"""PLN Search - CLI tool for searching the PLN Directory API."""

__version__ = "0.1.0"
```

**Step 2: Create main entry point**

File: `pln_search/__main__.py`
```python
"""Entry point for python -m pln_search."""

from pln_search.cli import main

if __name__ == "__main__":
    main()
```

**Step 3: Create tests directory**

File: `tests/__init__.py`
```python
"""Tests for pln-search."""
```

**Step 4: Install dependencies**

```bash
uv pip install -e .
```

Expected: Package installed in editable mode

**Step 5: Verify installation**

```bash
python -m pln_search
```

Expected: Error (no CLI yet) - that's fine

**Step 6: Commit package structure**

```bash
git add pln_search/ tests/
git commit -m "feat: create package structure"
```

---

### Task 4: Implement Data Models

**Files:**
- Create: `~/Public/src/dob/pln-search/pln_search/models.py`
- Create: `~/Public/src/dob/pln-search/tests/test_models.py`

**Step 1: Write test for Member model**

File: `tests/test_models.py`
```python
"""Tests for data models."""

from pln_search.models import Member, Team, Project


def test_member_creation():
    """Test Member dataclass creation."""
    member = Member(
        uid="m123",
        name="John Doe",
        email="john@example.com",
        bio="Software engineer",
        location="San Francisco, CA",
        skills=["Python", "Rust"],
        github_handler="johndoe",
    )
    assert member.uid == "m123"
    assert member.name == "John Doe"
    assert len(member.skills) == 2


def test_member_optional_fields():
    """Test Member with optional fields as None."""
    member = Member(
        uid="m123",
        name="Jane Doe",
        email=None,
        bio=None,
        location=None,
        skills=[],
        github_handler=None,
    )
    assert member.email is None
    assert member.bio is None
```

**Step 2: Run test to verify it fails**

```bash
pytest tests/test_models.py -v
```

Expected: FAIL - ImportError: cannot import name 'Member'

**Step 3: Implement Member model**

File: `pln_search/models.py`
```python
"""Data models for PLN API responses."""

from dataclasses import dataclass


@dataclass
class Member:
    """Member entity from PLN directory."""

    uid: str
    name: str
    email: str | None
    bio: str | None
    location: str | None
    skills: list[str]
    github_handler: str | None


@dataclass
class Team:
    """Team entity from PLN directory."""

    uid: str
    name: str
    short_description: str | None
    website: str | None
    member_count: int


@dataclass
class Project:
    """Project entity from PLN directory."""

    uid: str
    name: str
    description: str | None
    maintaining_team: str | None
    looking_for_funding: bool
```

**Step 4: Run test to verify it passes**

```bash
pytest tests/test_models.py -v
```

Expected: PASS (2 tests)

**Step 5: Add tests for Team and Project**

Append to `tests/test_models.py`:
```python


def test_team_creation():
    """Test Team dataclass creation."""
    team = Team(
        uid="t123",
        name="Protocol Labs",
        short_description="Building the future of the internet",
        website="https://protocol.ai",
        member_count=50,
    )
    assert team.uid == "t123"
    assert team.member_count == 50


def test_project_creation():
    """Test Project dataclass creation."""
    project = Project(
        uid="p123",
        name="IPFS",
        description="InterPlanetary File System",
        maintaining_team="Protocol Labs",
        looking_for_funding=False,
    )
    assert project.uid == "p123"
    assert project.looking_for_funding is False
```

**Step 6: Run all model tests**

```bash
pytest tests/test_models.py -v
```

Expected: PASS (4 tests)

**Step 7: Commit models**

```bash
git add pln_search/models.py tests/test_models.py
git commit -m "feat: add data models for Member, Team, Project"
```

---

### Task 5: Implement Configuration Manager

**Files:**
- Create: `~/Public/src/dob/pln-search/pln_search/config.py`
- Create: `~/Public/src/dob/pln-search/tests/test_config.py`

**Step 1: Write test for config directory**

File: `tests/test_config.py`
```python
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
```

**Step 2: Run test to verify it fails**

```bash
pytest tests/test_config.py -v
```

Expected: FAIL - ImportError: cannot import name 'ConfigManager'

**Step 3: Implement ConfigManager**

File: `pln_search/config.py`
```python
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
        return os.environ.get("PLN_API_URL", "https://api.pln.network")
```

**Step 4: Run test to verify it passes**

```bash
pytest tests/test_config.py -v
```

Expected: PASS (4 tests)

**Step 5: Commit config manager**

```bash
git add pln_search/config.py tests/test_config.py
git commit -m "feat: add configuration manager with credential storage"
```

---

### Task 6: Implement API Client (Basic Structure)

**Files:**
- Create: `~/Public/src/dob/pln-search/pln_search/api.py`
- Create: `~/Public/src/dob/pln-search/tests/test_api.py`

**Step 1: Write test for API client initialization**

File: `tests/test_api.py`
```python
"""Tests for API client."""

from unittest.mock import Mock
from pln_search.api import PLNAPIClient


def test_client_initialization():
    """Test API client can be initialized."""
    mock_auth = Mock()
    mock_auth.get_valid_token.return_value = "test_token"

    client = PLNAPIClient(
        base_url="https://api.test.com",
        auth=mock_auth
    )

    assert client.base_url == "https://api.test.com"
    assert client.auth == mock_auth
```

**Step 2: Run test to verify it fails**

```bash
pytest tests/test_api.py -v
```

Expected: FAIL - ImportError: cannot import name 'PLNAPIClient'

**Step 3: Implement basic API client**

File: `pln_search/api.py`
```python
"""API client for PLN Directory API."""

import requests
from typing import Any
from pln_search.models import Member, Team, Project


class APIError(Exception):
    """Base exception for API errors."""
    pass


class AuthenticationError(APIError):
    """Authentication failed or token expired."""
    pass


class PLNAPIClient:
    """Client for interacting with PLN Directory API."""

    def __init__(self, base_url: str, auth: Any):
        """Initialize API client.

        Args:
            base_url: Base URL for API (e.g., https://api.pln.network)
            auth: Authentication provider with get_valid_token() method
        """
        self.base_url = base_url.rstrip("/")
        self.auth = auth
        self.timeout = 30

    def _get_headers(self) -> dict[str, str]:
        """Get headers with authentication token.

        Returns:
            Headers dict with Authorization
        """
        token = self.auth.get_valid_token()
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

    def _make_request(self, method: str, endpoint: str, **kwargs) -> dict:
        """Make HTTP request to API.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint (e.g., /v1/members)
            **kwargs: Additional arguments for requests

        Returns:
            JSON response as dict

        Raises:
            AuthenticationError: If 401/403 received
            APIError: For other HTTP errors
        """
        url = f"{self.base_url}{endpoint}"
        headers = self._get_headers()

        try:
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                timeout=self.timeout,
                **kwargs
            )

            if response.status_code == 401:
                raise AuthenticationError("Authentication required. Run: pln-search auth")

            if response.status_code == 403:
                raise AuthenticationError("Access denied. Check permissions.")

            response.raise_for_status()

            return response.json()

        except requests.exceptions.Timeout:
            raise APIError("Request timed out. Try again later.")
        except requests.exceptions.ConnectionError:
            raise APIError("Cannot reach PLN API. Check connection.")
        except requests.exceptions.HTTPError as e:
            if e.response.status_code >= 500:
                raise APIError(f"API error ({e.response.status_code}). Try again later.")
            raise APIError(f"API request failed: {e}")

    def search_members(self, query: str, limit: int = 20) -> list[Member]:
        """Search for members by name or keyword.

        Args:
            query: Search query
            limit: Maximum results to return

        Returns:
            List of Member objects
        """
        # TODO: Implement in next task
        raise NotImplementedError()

    def search_teams(self, query: str, limit: int = 20) -> list[Team]:
        """Search for teams by name.

        Args:
            query: Search query
            limit: Maximum results to return

        Returns:
            List of Team objects
        """
        # TODO: Implement in next task
        raise NotImplementedError()

    def search_projects(self, query: str, limit: int = 20) -> list[Project]:
        """Search for projects by name.

        Args:
            query: Search query
            limit: Maximum results to return

        Returns:
            List of Project objects
        """
        # TODO: Implement in next task
        raise NotImplementedError()

    def global_search(self, query: str) -> dict[str, Any]:
        """Search across all entity types.

        Args:
            query: Search query

        Returns:
            Dict with members, teams, projects keys
        """
        # TODO: Implement in next task
        raise NotImplementedError()
```

**Step 4: Run test to verify it passes**

```bash
pytest tests/test_api.py -v
```

Expected: PASS (1 test)

**Step 5: Commit API client structure**

```bash
git add pln_search/api.py tests/test_api.py
git commit -m "feat: add API client structure with error handling"
```

---

### Task 7: Implement API Search Methods

**Files:**
- Modify: `~/Public/src/dob/pln-search/pln_search/api.py`
- Modify: `~/Public/src/dob/pln-search/tests/test_api.py`

**Step 1: Write test for member search**

Append to `tests/test_api.py`:
```python
from unittest.mock import patch, Mock


def test_search_members(requests_mock):
    """Test searching for members."""
    mock_auth = Mock()
    mock_auth.get_valid_token.return_value = "test_token"

    # Mock API response
    requests_mock.get(
        "https://api.test.com/v1/members/search",
        json={
            "members": [
                {
                    "uid": "m123",
                    "name": "John Doe",
                    "email": "john@example.com",
                    "bio": "Engineer",
                    "location": {"city": "SF", "country": "USA"},
                    "skills": [{"title": "Python"}, {"title": "Rust"}],
                    "githubHandler": "johndoe"
                }
            ],
            "total": 1
        }
    )

    client = PLNAPIClient("https://api.test.com", mock_auth)
    results = client.search_members("John", limit=20)

    assert len(results) == 1
    assert results[0].name == "John Doe"
    assert results[0].uid == "m123"
    assert "Python" in results[0].skills
```

**Step 2: Install test dependency**

```bash
uv add --dev pytest-mock requests-mock
```

**Step 3: Run test to verify it fails**

```bash
pytest tests/test_api.py::test_search_members -v
```

Expected: FAIL - NotImplementedError

**Step 4: Implement search_members**

Replace the `search_members` method in `pln_search/api.py`:
```python
    def search_members(self, query: str, limit: int = 20) -> list[Member]:
        """Search for members by name or keyword.

        Args:
            query: Search query
            limit: Maximum results to return

        Returns:
            List of Member objects
        """
        params = {"q": query, "limit": limit}
        data = self._make_request("GET", "/v1/members/search", params=params)

        members = []
        for item in data.get("members", []):
            # Extract location string
            location = None
            if item.get("location"):
                loc = item["location"]
                city = loc.get("city", "")
                country = loc.get("country", "")
                location = f"{city}, {country}".strip(", ")

            # Extract skill titles
            skills = [s["title"] for s in item.get("skills", [])]

            member = Member(
                uid=item["uid"],
                name=item["name"],
                email=item.get("email"),
                bio=item.get("bio"),
                location=location,
                skills=skills,
                github_handler=item.get("githubHandler"),
            )
            members.append(member)

        return members
```

**Step 5: Run test to verify it passes**

```bash
pytest tests/test_api.py::test_search_members -v
```

Expected: PASS

**Step 6: Add tests and implementations for teams and projects**

Append to `tests/test_api.py`:
```python


def test_search_teams(requests_mock):
    """Test searching for teams."""
    mock_auth = Mock()
    mock_auth.get_valid_token.return_value = "test_token"

    requests_mock.get(
        "https://api.test.com/v1/teams",
        json=[
            {
                "uid": "t123",
                "name": "Protocol Labs",
                "shortDescription": "Building the future",
                "website": "https://protocol.ai",
                "teamMemberRoles": [{"uid": "1"}, {"uid": "2"}]
            }
        ]
    )

    client = PLNAPIClient("https://api.test.com", mock_auth)
    results = client.search_teams("Protocol", limit=20)

    assert len(results) == 1
    assert results[0].name == "Protocol Labs"
    assert results[0].member_count == 2


def test_search_projects(requests_mock):
    """Test searching for projects."""
    mock_auth = Mock()
    mock_auth.get_valid_token.return_value = "test_token"

    requests_mock.get(
        "https://api.test.com/v1/projects",
        json=[
            {
                "uid": "p123",
                "name": "IPFS",
                "description": "InterPlanetary File System",
                "maintainingTeam": {"name": "Protocol Labs"},
                "lookingForFunding": False
            }
        ]
    )

    client = PLNAPIClient("https://api.test.com", mock_auth)
    results = client.search_projects("IPFS", limit=20)

    assert len(results) == 1
    assert results[0].name == "IPFS"
    assert results[0].maintaining_team == "Protocol Labs"
```

**Step 7: Implement search_teams and search_projects**

Replace methods in `pln_search/api.py`:
```python
    def search_teams(self, query: str, limit: int = 20) -> list[Team]:
        """Search for teams by name.

        Args:
            query: Search query
            limit: Maximum results to return

        Returns:
            List of Team objects
        """
        params = {"name__icontains": query, "limit": limit}
        data = self._make_request("GET", "/v1/teams", params=params)

        teams = []
        for item in data if isinstance(data, list) else []:
            team = Team(
                uid=item["uid"],
                name=item["name"],
                short_description=item.get("shortDescription"),
                website=item.get("website"),
                member_count=len(item.get("teamMemberRoles", [])),
            )
            teams.append(team)

        return teams

    def search_projects(self, query: str, limit: int = 20) -> list[Project]:
        """Search for projects by name.

        Args:
            query: Search query
            limit: Maximum results to return

        Returns:
            List of Project objects
        """
        params = {"name__icontains": query, "limit": limit}
        data = self._make_request("GET", "/v1/projects", params=params)

        projects = []
        for item in data if isinstance(data, list) else []:
            # Extract team name
            team_name = None
            if item.get("maintainingTeam"):
                team_name = item["maintainingTeam"].get("name")

            project = Project(
                uid=item["uid"],
                name=item["name"],
                description=item.get("description"),
                maintaining_team=team_name,
                looking_for_funding=item.get("lookingForFunding", False),
            )
            projects.append(project)

        return projects
```

**Step 8: Run all API tests**

```bash
pytest tests/test_api.py -v
```

Expected: PASS (4 tests)

**Step 9: Commit search implementations**

```bash
git add pln_search/api.py tests/test_api.py
git commit -m "feat: implement member, team, and project search methods"
```

---

### Task 8: Implement Output Formatters

**Files:**
- Create: `~/Public/src/dob/pln-search/pln_search/formatters.py`
- Create: `~/Public/src/dob/pln-search/tests/test_formatters.py`

**Step 1: Write test for formatter initialization**

File: `tests/test_formatters.py`
```python
"""Tests for output formatters."""

import sys
from io import StringIO
from pln_search.formatters import OutputFormatter
from pln_search.models import Member, Team, Project


def test_formatter_auto_detection_tty(monkeypatch):
    """Test auto format detection for TTY."""
    monkeypatch.setattr(sys.stdout, "isatty", lambda: True)

    formatter = OutputFormatter(format_type="auto")
    assert formatter.format_type == "rich"


def test_formatter_auto_detection_pipe(monkeypatch):
    """Test auto format detection for pipe."""
    monkeypatch.setattr(sys.stdout, "isatty", lambda: False)

    formatter = OutputFormatter(format_type="auto")
    assert formatter.format_type == "plain"


def test_formatter_explicit_json():
    """Test explicit JSON format."""
    formatter = OutputFormatter(format_type="json")
    assert formatter.format_type == "json"
```

**Step 2: Run test to verify it fails**

```bash
pytest tests/test_formatters.py -v
```

Expected: FAIL - ImportError

**Step 3: Implement OutputFormatter base**

File: `pln_search/formatters.py`
```python
"""Output formatters for search results."""

import sys
import json
from typing import Literal
from rich.console import Console
from rich.table import Table
from pln_search.models import Member, Team, Project


FormatType = Literal["auto", "rich", "plain", "json"]


class OutputFormatter:
    """Format search results for different output modes."""

    def __init__(self, format_type: FormatType = "auto"):
        """Initialize formatter.

        Args:
            format_type: Output format type
        """
        if format_type == "auto":
            # Auto-detect: rich for TTY, plain for pipes
            self.format_type = "rich" if sys.stdout.isatty() else "plain"
        else:
            self.format_type = format_type

        self.console = Console()

    def format_members(self, members: list[Member]) -> None:
        """Format and print member results.

        Args:
            members: List of members to display
        """
        if not members:
            self._print_no_results("members")
            return

        if self.format_type == "json":
            self._format_members_json(members)
        elif self.format_type == "rich":
            self._format_members_rich(members)
        else:
            self._format_members_plain(members)

    def format_teams(self, teams: list[Team]) -> None:
        """Format and print team results.

        Args:
            teams: List of teams to display
        """
        if not teams:
            self._print_no_results("teams")
            return

        if self.format_type == "json":
            self._format_teams_json(teams)
        elif self.format_type == "rich":
            self._format_teams_rich(teams)
        else:
            self._format_teams_plain(teams)

    def format_projects(self, projects: list[Project]) -> None:
        """Format and print project results.

        Args:
            projects: List of projects to display
        """
        if not projects:
            self._print_no_results("projects")
            return

        if self.format_type == "json":
            self._format_projects_json(projects)
        elif self.format_type == "rich":
            self._format_projects_rich(projects)
        else:
            self._format_projects_plain(projects)

    def _print_no_results(self, entity_type: str) -> None:
        """Print no results message."""
        print(f"No {entity_type} found.")

    # JSON formatters
    def _format_members_json(self, members: list[Member]) -> None:
        """Format members as JSON."""
        data = [vars(m) for m in members]
        print(json.dumps(data, indent=2))

    def _format_teams_json(self, teams: list[Team]) -> None:
        """Format teams as JSON."""
        data = [vars(t) for t in teams]
        print(json.dumps(data, indent=2))

    def _format_projects_json(self, projects: list[Project]) -> None:
        """Format projects as JSON."""
        data = [vars(p) for p in projects]
        print(json.dumps(data, indent=2))

    # Rich formatters (tables)
    def _format_members_rich(self, members: list[Member]) -> None:
        """Format members as rich table."""
        table = Table(title=f"Members ({len(members)} results)")

        table.add_column("Name", style="cyan", no_wrap=True)
        table.add_column("Location", style="magenta")
        table.add_column("Skills", style="green")
        table.add_column("GitHub", style="blue")

        for member in members:
            skills_str = ", ".join(member.skills[:3])
            if len(member.skills) > 3:
                skills_str += f" +{len(member.skills) - 3} more"

            table.add_row(
                member.name,
                member.location or "-",
                skills_str or "-",
                member.github_handler or "-",
            )

        self.console.print(table)

    def _format_teams_rich(self, teams: list[Team]) -> None:
        """Format teams as rich table."""
        table = Table(title=f"Teams ({len(teams)} results)")

        table.add_column("Name", style="cyan", no_wrap=True)
        table.add_column("Description", style="white")
        table.add_column("Members", style="yellow", justify="right")
        table.add_column("Website", style="blue")

        for team in teams:
            desc = team.short_description or "-"
            if len(desc) > 50:
                desc = desc[:47] + "..."

            table.add_row(
                team.name,
                desc,
                str(team.member_count),
                team.website or "-",
            )

        self.console.print(table)

    def _format_projects_rich(self, projects: list[Project]) -> None:
        """Format projects as rich table."""
        table = Table(title=f"Projects ({len(projects)} results)")

        table.add_column("Name", style="cyan", no_wrap=True)
        table.add_column("Description", style="white")
        table.add_column("Team", style="magenta")
        table.add_column("Funding?", style="yellow")

        for project in projects:
            desc = project.description or "-"
            if len(desc) > 50:
                desc = desc[:47] + "..."

            table.add_row(
                project.name,
                desc,
                project.maintaining_team or "-",
                "Yes" if project.looking_for_funding else "No",
            )

        self.console.print(table)

    # Plain formatters (text)
    def _format_members_plain(self, members: list[Member]) -> None:
        """Format members as plain text."""
        print(f"Members ({len(members)} results):")
        print()
        for member in members:
            skills = ", ".join(member.skills[:3])
            if len(member.skills) > 3:
                skills += f" +{len(member.skills) - 3}"

            print(f"  {member.name}")
            if member.location:
                print(f"    Location: {member.location}")
            if skills:
                print(f"    Skills: {skills}")
            if member.github_handler:
                print(f"    GitHub: {member.github_handler}")
            print()

    def _format_teams_plain(self, teams: list[Team]) -> None:
        """Format teams as plain text."""
        print(f"Teams ({len(teams)} results):")
        print()
        for team in teams:
            print(f"  {team.name} ({team.member_count} members)")
            if team.short_description:
                print(f"    {team.short_description}")
            if team.website:
                print(f"    {team.website}")
            print()

    def _format_projects_plain(self, projects: list[Project]) -> None:
        """Format projects as plain text."""
        print(f"Projects ({len(projects)} results):")
        print()
        for project in projects:
            funding = " [Looking for funding]" if project.looking_for_funding else ""
            print(f"  {project.name}{funding}")
            if project.description:
                print(f"    {project.description}")
            if project.maintaining_team:
                print(f"    Team: {project.maintaining_team}")
            print()
```

**Step 4: Run tests**

```bash
pytest tests/test_formatters.py -v
```

Expected: PASS (3 tests)

**Step 5: Add output tests**

Append to `tests/test_formatters.py`:
```python
from unittest.mock import patch


def test_format_members_json():
    """Test JSON formatting for members."""
    members = [
        Member(
            uid="m1",
            name="John Doe",
            email="john@example.com",
            bio="Engineer",
            location="SF",
            skills=["Python"],
            github_handler="john",
        )
    ]

    formatter = OutputFormatter(format_type="json")

    with patch("builtins.print") as mock_print:
        formatter.format_members(members)
        output = mock_print.call_args[0][0]
        assert "John Doe" in output
        assert "m1" in output


def test_format_members_plain():
    """Test plain text formatting for members."""
    members = [
        Member(
            uid="m1",
            name="Jane Doe",
            email=None,
            bio=None,
            location="NYC",
            skills=["Rust", "Go"],
            github_handler=None,
        )
    ]

    formatter = OutputFormatter(format_type="plain")

    with patch("builtins.print") as mock_print:
        formatter.format_members(members)
        # Check print was called with member info
        calls = [str(call) for call in mock_print.call_args_list]
        output = " ".join(calls)
        assert "Jane Doe" in output
        assert "NYC" in output
```

**Step 6: Run all formatter tests**

```bash
pytest tests/test_formatters.py -v
```

Expected: PASS (5 tests)

**Step 7: Commit formatters**

```bash
git add pln_search/formatters.py tests/test_formatters.py
git commit -m "feat: implement output formatters (rich, plain, JSON)"
```

---

### Task 9: Implement OAuth2 Authentication (Stub for CLI)

**Files:**
- Create: `~/Public/src/dob/pln-search/pln_search/auth.py`
- Create: `~/Public/src/dob/pln-search/tests/test_auth.py`

**Note:** Full OAuth2 flow requires browser integration and localhost server. For now, implement a stub that reads/refreshes tokens. Browser flow will be implemented when testing with real API.

**Step 1: Write test for token validation**

File: `tests/test_auth.py`
```python
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
```

**Step 2: Run test to verify it fails**

```bash
pytest tests/test_auth.py -v
```

Expected: FAIL - ImportError

**Step 3: Implement OAuth2Flow stub**

File: `pln_search/auth.py`
```python
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

    def start_auth_flow(self) -> None:
        """Start OAuth2 browser authentication flow.

        This will:
        1. Create auth request
        2. Open browser to consent page
        3. Start localhost server
        4. Exchange code for tokens
        5. Save credentials
        """
        # TODO: Implement full OAuth2 flow
        # For now, print instructions
        print("OAuth2 browser flow not yet implemented.")
        print("Manual token entry:")
        print("1. Obtain access token from PLN API")
        print("2. Save to credentials manually")
        raise NotImplementedError("Full OAuth2 flow coming soon")
```

**Step 4: Run tests**

```bash
pytest tests/test_auth.py -v
```

Expected: PASS (2 tests)

**Step 5: Commit auth stub**

```bash
git add pln_search/auth.py tests/test_auth.py
git commit -m "feat: add OAuth2 authentication with token refresh"
```

---

### Task 10: Implement CLI Commands

**Files:**
- Create: `~/Public/src/dob/pln-search/pln_search/cli.py`
- Modify: `~/Public/src/dob/pln-search/tests/test_cli.py`

**Step 1: Write test for CLI help**

File: `tests/test_cli.py`
```python
"""Tests for CLI commands."""

from click.testing import CliRunner
from pln_search.cli import main


def test_cli_help():
    """Test CLI help output."""
    runner = CliRunner()
    result = runner.invoke(main, ["--help"])

    assert result.exit_code == 0
    assert "pln-search" in result.output.lower()


def test_cli_version():
    """Test version command."""
    runner = CliRunner()
    result = runner.invoke(main, ["--version"])

    assert result.exit_code == 0
    assert "0.1.0" in result.output
```

**Step 2: Run test to verify it fails**

```bash
pytest tests/test_cli.py -v
```

Expected: FAIL - ImportError

**Step 3: Implement CLI**

File: `pln_search/cli.py`
```python
"""Command-line interface for pln-search."""

import sys
import click
from pln_search import __version__
from pln_search.config import ConfigManager
from pln_search.auth import OAuth2Flow, AuthenticationError
from pln_search.api import PLNAPIClient, APIError
from pln_search.formatters import OutputFormatter


@click.group(invoke_without_command=True)
@click.option("--members", "search_type", flag_value="members", help="Search members only")
@click.option("--teams", "search_type", flag_value="teams", help="Search teams only")
@click.option("--projects", "search_type", flag_value="projects", help="Search projects only")
@click.option("--limit", default=20, help="Maximum results to show", type=int)
@click.option("--json", "output_json", is_flag=True, help="Output JSON")
@click.option("--no-color", is_flag=True, help="Plain text output")
@click.option("--version", is_flag=True, help="Show version")
@click.argument("query", required=False)
@click.pass_context
def main(ctx, search_type, limit, output_json, no_color, version, query):
    """PLN Search - Search the PLN Directory API.

    Examples:
        pln-search "John Doe"                 # Global search
        pln-search --members "John"           # Search members
        pln-search --teams "Protocol"         # Search teams
        pln-search --projects "IPFS"          # Search projects
        pln-search "query" --json             # JSON output
    """
    # Handle version flag
    if version:
        click.echo(f"pln-search version {__version__}")
        return

    # If no query and no subcommand, show help
    if not query and ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())
        return

    # Only run search if query provided
    if query:
        try:
            _run_search(query, search_type, limit, output_json, no_color)
        except AuthenticationError as e:
            click.echo(f"✗ {e}", err=True)
            sys.exit(2)
        except APIError as e:
            click.echo(f"✗ {e}", err=True)
            sys.exit(1)
        except Exception as e:
            click.echo(f"✗ Unexpected error: {e}", err=True)
            sys.exit(1)


def _run_search(query: str, search_type: str, limit: int, output_json: bool, no_color: bool):
    """Run search and display results."""
    # Initialize components
    config = ConfigManager()
    auth = OAuth2Flow(config.get_api_base_url(), config)
    client = PLNAPIClient(config.get_api_base_url(), auth)

    # Determine output format
    if output_json:
        format_type = "json"
    elif no_color:
        format_type = "plain"
    else:
        format_type = "auto"

    formatter = OutputFormatter(format_type)

    # Execute search based on type
    if search_type == "members":
        results = client.search_members(query, limit)
        formatter.format_members(results)
    elif search_type == "teams":
        results = client.search_teams(query, limit)
        formatter.format_teams(results)
    elif search_type == "projects":
        results = client.search_projects(query, limit)
        formatter.format_projects(results)
    else:
        # Global search - search all types
        members = client.search_members(query, limit)
        teams = client.search_teams(query, limit)
        projects = client.search_projects(query, limit)

        formatter.format_members(members)
        formatter.format_teams(teams)
        formatter.format_projects(projects)


@main.group()
def auth():
    """Authentication commands."""
    pass


@auth.command("login")
def auth_login():
    """Start OAuth2 authentication flow."""
    try:
        config = ConfigManager()
        auth_flow = OAuth2Flow(config.get_api_base_url(), config)
        auth_flow.start_auth_flow()
    except Exception as e:
        click.echo(f"✗ Authentication failed: {e}", err=True)
        sys.exit(1)


@auth.command("status")
def auth_status():
    """Check authentication status."""
    config = ConfigManager()
    creds = config.load_credentials()

    if creds:
        user_info = creds.get("user_info", {})
        click.echo("✓ Authenticated")
        if user_info.get("name"):
            click.echo(f"  User: {user_info['name']}")
        if user_info.get("email"):
            click.echo(f"  Email: {user_info['email']}")
    else:
        click.echo("✗ Not authenticated")
        click.echo("  Run: pln-search auth login")
        sys.exit(2)


@auth.command("logout")
def auth_logout():
    """Remove stored credentials."""
    config = ConfigManager()
    config.clear_credentials()
    click.echo("✓ Logged out")


if __name__ == "__main__":
    main()
```

**Step 4: Run tests**

```bash
pytest tests/test_cli.py -v
```

Expected: PASS (2 tests)

**Step 5: Test CLI manually**

```bash
pln-search --help
pln-search --version
pln-search auth --help
```

Expected: Commands work and show help

**Step 6: Commit CLI**

```bash
git add pln_search/cli.py tests/test_cli.py
git commit -m "feat: implement CLI with search and auth commands"
```

---

### Task 11: Create Makefile

**Files:**
- Create: `~/Public/src/dob/pln-search/Makefile`

**Step 1: Create Makefile**

File: `Makefile`
```makefile
.PHONY: help install install-dev test clean build format lint check run
.DEFAULT_GOAL := help

PYTHON := python
UV := uv
PACKAGE_NAME := pln-search

help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-20s %s\n", $$1, $$2}'

install: ## Install package in development mode
	$(UV) pip install -e .

install-dev: ## Install with dev dependencies
	$(UV) pip install -e ".[dev]"
	$(UV) add --dev pytest pytest-mock requests-mock ruff

test: ## Run tests
	$(PYTHON) -m pytest tests/ -v

test-coverage: ## Run tests with coverage
	$(UV) add --dev coverage
	coverage run -m pytest tests/
	coverage report
	coverage html

lint: ## Run linting
	$(UV) run ruff check .

format: ## Format code
	$(UV) run ruff format .

lint-fix: ## Run linting with auto-fix
	$(UV) run ruff check . --fix

check: lint test ## Run linting and tests

check-fix: lint-fix format test ## Fix lint issues, format, and test

clean: ## Clean build artifacts
	rm -rf build/ dist/ *.egg-info/ .pytest_cache/
	rm -rf .coverage htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

build: clean ## Build distribution
	$(UV) build

run: ## Run pln-search (development)
	$(UV) run pln-search

auth: ## Run authentication flow
	$(UV) run pln-search auth login

auth-status: ## Check auth status
	$(UV) run pln-search auth status

search-test: ## Run a test search (requires auth)
	$(UV) run pln-search --members "test"

dev-setup: install-dev ## Complete development setup
	@echo "Development environment ready!"
	@echo "Run 'make test' to run tests"
	@echo "Run 'make check' to run linting and tests"
```

**Step 2: Test Makefile targets**

```bash
make help
make install
make test
```

Expected: All targets work

**Step 3: Commit Makefile**

```bash
git add Makefile
git commit -m "chore: add Makefile for development tasks"
```

---

### Task 12: Final Integration Testing

**Files:**
- Modify: `~/Public/src/dob/pln-search/README.md` (add testing notes)

**Step 1: Run full test suite**

```bash
make test
```

Expected: All tests pass

**Step 2: Test CLI help**

```bash
pln-search --help
pln-search auth --help
pln-search auth status
```

Expected: Commands work correctly

**Step 3: Update README with development status**

Append to `README.md`:
```markdown

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
```

**Step 4: Commit final changes**

```bash
git add README.md
git commit -m "docs: update README with development status"
```

**Step 5: Tag release**

```bash
git tag -a v0.1.0 -m "Initial implementation - core functionality complete"
```

---

## Next Steps

The core implementation is complete. To use with the real PLN API:

1. **Implement full OAuth2 browser flow** in `auth.py`:
   - Add localhost HTTP server (port 8765)
   - Open browser to consent page
   - Handle callback with auth code
   - Exchange code for tokens

2. **Test with real API**:
   - Set `PLN_API_URL` environment variable
   - Run authentication flow
   - Test all search commands

3. **Refinements**:
   - Add pagination support
   - Improve error messages
   - Add caching (optional)
   - Performance testing

4. **Distribution**:
   - Build with `make build`
   - Test installation from wheel
   - Consider PyPI publishing

## Dependencies Summary

All dependencies installed via `uv`:
- click (CLI framework)
- requests (HTTP client)
- rich (terminal formatting)
- platformdirs (XDG config paths)
- pytest, pytest-mock, requests-mock (testing)
- ruff (linting/formatting)
