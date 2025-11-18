"""Tests for API client."""

from unittest.mock import Mock, patch
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


def test_search_members(requests_mock):
    """Test searching for members."""
    mock_auth = Mock()
    mock_auth.get_valid_token.return_value = "test_token"

    # Mock API response
    requests_mock.get(
        "https://api.test.com/v1/members",
        json={
            "count": 1,
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
            ]
        }
    )

    client = PLNAPIClient("https://api.test.com", mock_auth)
    results = client.search_members("John", limit=20)

    assert len(results) == 1
    assert results[0].name == "John Doe"
    assert results[0].uid == "m123"
    assert "Python" in results[0].skills


def test_search_teams(requests_mock):
    """Test searching for teams with real API response format."""
    mock_auth = Mock()
    mock_auth.get_valid_token.return_value = "test_token"

    # Real API returns {"count": N, "teams": [...]}
    requests_mock.get(
        "https://api.test.com/v1/teams",
        json={
            "count": 1,
            "teams": [
                {
                    "uid": "t123",
                    "name": "Protocol Labs",
                    "shortDescription": "Building the future",
                    "website": "https://protocol.ai",
                    "teamMemberRoles": [{"uid": "1"}, {"uid": "2"}]
                }
            ]
        }
    )

    client = PLNAPIClient("https://api.test.com", mock_auth)
    results = client.search_teams("Protocol", limit=20)

    assert len(results) == 1
    assert results[0].name == "Protocol Labs"
    assert results[0].member_count == 2


def test_search_projects(requests_mock):
    """Test searching for projects with real API response format."""
    mock_auth = Mock()
    mock_auth.get_valid_token.return_value = "test_token"

    # Real API returns {"count": N, "projects": [...]}
    requests_mock.get(
        "https://api.test.com/v1/projects",
        json={
            "count": 1,
            "projects": [
                {
                    "uid": "p123",
                    "name": "IPFS",
                    "description": "InterPlanetary File System",
                    "maintainingTeam": {"name": "Protocol Labs"},
                    "lookingForFunding": False
                }
            ]
        }
    )

    client = PLNAPIClient("https://api.test.com", mock_auth)
    results = client.search_projects("IPFS", limit=20)

    assert len(results) == 1
    assert results[0].name == "IPFS"
    assert results[0].maintaining_team == "Protocol Labs"
