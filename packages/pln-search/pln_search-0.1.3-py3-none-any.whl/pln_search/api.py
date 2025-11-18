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
        params = {"name__icontains": query, "limit": limit}
        data = self._make_request("GET", "/v1/members", params=params)

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
                discord_handler=item.get("discordHandler"),
                telegram_handler=item.get("telegramHandler"),
                office_hours=item.get("officeHours"),
            )
            members.append(member)

        return members

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
        for item in data.get("teams", []):
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
        for item in data.get("projects", []):
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

    def global_search(self, query: str) -> dict[str, Any]:
        """Search across all entity types.

        Args:
            query: Search query

        Returns:
            Dict with members, teams, projects keys
        """
        # TODO: Implement in next task
        raise NotImplementedError()
