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

    def _make_link(self, text: str, url: str) -> str:
        """Wrap text in Rich hyperlink markup.

        Args:
            text: Display text
            url: URL to link to

        Returns:
            Text wrapped in Rich link markup (rich mode) or plain text (other modes)
        """
        if self.format_type != "rich":
            return text
        # Use Rich's built-in link markup to avoid table formatting issues
        return f"[link={url}]{text}[/link]"

    def _make_directory_url(self, entity_type: str, uid: str) -> str:
        """Generate PLN Directory profile URL.

        Args:
            entity_type: Type of entity ("members", "teams", "projects")
            uid: Entity UID

        Returns:
            Full PLN Directory URL
        """
        return f"https://directory.plnetwork.io/{entity_type}/{uid}"

    def _make_github_url(self, github_handler: str) -> str:
        """Generate GitHub profile URL.

        Args:
            github_handler: GitHub username

        Returns:
            Full GitHub profile URL
        """
        return f"https://github.com/{github_handler}"

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
        table.add_column("Contact", style="magenta")
        table.add_column("Office Hours", style="green")
        table.add_column("GitHub", style="blue")

        for member in members:
            # Make name clickable (links to directory profile)
            name = self._make_link(
                member.name,
                self._make_directory_url("members", member.uid)
            )

            # Build contact info (multi-line) with clickable links
            contact_lines = []
            if member.email:
                email_link = self._make_link(member.email, f"mailto:{member.email}")
                contact_lines.append(email_link)
            if member.discord_handler:
                # Discord requires numeric user ID for links, so keep as plain text
                contact_lines.append(f"Discord: {member.discord_handler}")
            if member.telegram_handler:
                telegram_link = self._make_link(
                    f"Telegram: {member.telegram_handler}",
                    f"https://t.me/{member.telegram_handler}"
                )
                contact_lines.append(telegram_link)
            contact = "\n".join(contact_lines) if contact_lines else "-"

            # Make office hours clickable if present
            office_hours = "-"
            if member.office_hours:
                office_hours = self._make_link("Book", member.office_hours)

            # Make GitHub handle clickable if present
            github = member.github_handler or "-"
            if member.github_handler:
                github = self._make_link(
                    member.github_handler,
                    self._make_github_url(member.github_handler)
                )

            table.add_row(
                name,
                contact,
                office_hours,
                github,
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

            # Make team name clickable (links to directory team page)
            name = self._make_link(
                team.name,
                self._make_directory_url("teams", team.uid)
            )

            table.add_row(
                name,
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

            # Make project name clickable (links to directory project page)
            name = self._make_link(
                project.name,
                self._make_directory_url("projects", project.uid)
            )

            table.add_row(
                name,
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
            print(f"  {member.name}")
            if member.email:
                print(f"    Email: {member.email}")
            if member.discord_handler:
                print(f"    Discord: {member.discord_handler}")
            if member.telegram_handler:
                print(f"    Telegram: {member.telegram_handler}")
            if member.office_hours:
                print(f"    Office Hours: {member.office_hours}")
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
