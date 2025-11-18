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


def test_format_members_json():
    """Test JSON formatting for members."""
    from unittest.mock import patch

    members = [
        Member(
            uid="m1",
            name="John Doe",
            email="john@example.com",
            bio="Engineer",
            location="SF",
            skills=["Python"],
            github_handler="john",
            discord_handler="johndoe",
            telegram_handler="johndoe",
            office_hours="https://calendly.com/john",
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
    from unittest.mock import patch

    members = [
        Member(
            uid="m1",
            name="Jane Doe",
            email=None,
            bio=None,
            location="NYC",
            skills=["Rust", "Go"],
            github_handler=None,
            discord_handler=None,
            telegram_handler=None,
            office_hours=None,
        )
    ]

    formatter = OutputFormatter(format_type="plain")

    with patch("builtins.print") as mock_print:
        formatter.format_members(members)
        # Check print was called with member info
        calls = [str(call) for call in mock_print.call_args_list]
        output = " ".join(calls)
        assert "Jane Doe" in output


def test_make_link_in_rich_mode():
    """Test Rich link markup generation in rich mode."""
    formatter = OutputFormatter(format_type="rich")

    result = formatter._make_link("Click me", "https://example.com")

    # Should contain Rich link markup
    assert result == "[link=https://example.com]Click me[/link]"


def test_make_link_in_plain_mode():
    """Test link generation returns plain text in plain mode."""
    formatter = OutputFormatter(format_type="plain")

    result = formatter._make_link("Click me", "https://example.com")

    # Should return plain text without escape codes
    assert result == "Click me"


def test_make_link_in_json_mode():
    """Test link generation returns plain text in JSON mode."""
    formatter = OutputFormatter(format_type="json")

    result = formatter._make_link("Click me", "https://example.com")

    # Should return plain text without escape codes
    assert result == "Click me"


def test_make_directory_url_for_members():
    """Test directory URL generation for members."""
    formatter = OutputFormatter(format_type="rich")

    result = formatter._make_directory_url("members", "abc123")

    assert result == "https://directory.plnetwork.io/members/abc123"


def test_make_directory_url_for_teams():
    """Test directory URL generation for teams."""
    formatter = OutputFormatter(format_type="rich")

    result = formatter._make_directory_url("teams", "team456")

    assert result == "https://directory.plnetwork.io/teams/team456"


def test_make_directory_url_for_projects():
    """Test directory URL generation for projects."""
    formatter = OutputFormatter(format_type="rich")

    result = formatter._make_directory_url("projects", "proj789")

    assert result == "https://directory.plnetwork.io/projects/proj789"


def test_make_github_url():
    """Test GitHub URL generation."""
    formatter = OutputFormatter(format_type="rich")

    result = formatter._make_github_url("octocat")

    assert result == "https://github.com/octocat"


def test_format_members_rich_with_hyperlinks():
    """Test that member names and GitHub handles become clickable in rich mode."""
    from unittest.mock import patch
    from rich.table import Table

    members = [
        Member(
            uid="m123",
            name="John Doe",
            email="john@example.com",
            bio="Engineer",
            location="SF",
            skills=["Python"],
            github_handler="johndoe",
            discord_handler="johndoe#1234",
            telegram_handler="johndoe_tg",
            office_hours="https://calendly.com/johndoe",
        )
    ]

    formatter = OutputFormatter(format_type="rich")

    # Capture what gets added to the table
    with patch.object(Table, "add_row") as mock_add_row:
        with patch.object(formatter.console, "print"):
            formatter.format_members(members)

    # Verify add_row was called with hyperlinked values
    call_args = mock_add_row.call_args[0]
    name_arg = call_args[0]
    contact_arg = call_args[1]
    office_hours_arg = call_args[2]
    github_arg = call_args[3]

    # Name should contain Rich link markup to directory profile
    assert "[link=https://directory.plnetwork.io/members/m123]" in name_arg
    assert "John Doe" in name_arg

    # Contact should contain clickable email and telegram, plain discord
    assert "[link=mailto:john@example.com]john@example.com[/link]" in contact_arg
    assert "Discord: johndoe#1234" in contact_arg  # Plain text, no link
    assert "[link=https://t.me/johndoe_tg]Telegram: johndoe_tg[/link]" in contact_arg

    # Office hours should be clickable
    assert "[link=https://calendly.com/johndoe]Book[/link]" in office_hours_arg

    # GitHub should contain Rich link markup to GitHub profile
    assert "[link=https://github.com/johndoe]" in github_arg
    assert "johndoe" in github_arg


def test_format_teams_rich_with_hyperlinks():
    """Test that team names become clickable in rich mode."""
    from unittest.mock import patch
    from rich.table import Table

    teams = [
        Team(
            uid="t456",
            name="Protocol Labs",
            short_description="Building the future",
            website="https://protocol.ai",
            member_count=50,
        )
    ]

    formatter = OutputFormatter(format_type="rich")

    # Capture what gets added to the table
    with patch.object(Table, "add_row") as mock_add_row:
        with patch.object(formatter.console, "print"):
            formatter.format_teams(teams)

    # Verify add_row was called with hyperlinked team name
    call_args = mock_add_row.call_args[0]
    name_arg = call_args[0]

    # Name should contain Rich link markup to directory team page
    assert "[link=https://directory.plnetwork.io/teams/t456]" in name_arg
    assert "Protocol Labs" in name_arg


def test_format_projects_rich_with_hyperlinks():
    """Test that project names become clickable in rich mode."""
    from unittest.mock import patch
    from rich.table import Table

    projects = [
        Project(
            uid="p789",
            name="IPFS",
            description="InterPlanetary File System",
            maintaining_team="Protocol Labs",
            looking_for_funding=False,
        )
    ]

    formatter = OutputFormatter(format_type="rich")

    # Capture what gets added to the table
    with patch.object(Table, "add_row") as mock_add_row:
        with patch.object(formatter.console, "print"):
            formatter.format_projects(projects)

    # Verify add_row was called with hyperlinked project name
    call_args = mock_add_row.call_args[0]
    name_arg = call_args[0]

    # Name should contain Rich link markup to directory project page
    assert "[link=https://directory.plnetwork.io/projects/p789]" in name_arg
    assert "IPFS" in name_arg
