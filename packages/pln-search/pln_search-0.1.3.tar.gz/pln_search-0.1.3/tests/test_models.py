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
        discord_handler="johndoe#1234",
        telegram_handler="johndoe",
        office_hours="https://calendly.com/johndoe",
    )
    assert member.uid == "m123"
    assert member.name == "John Doe"
    assert len(member.skills) == 2
    assert member.discord_handler == "johndoe#1234"
    assert member.office_hours == "https://calendly.com/johndoe"


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
        discord_handler=None,
        telegram_handler=None,
        office_hours=None,
    )
    assert member.email is None
    assert member.bio is None
    assert member.discord_handler is None
    assert member.office_hours is None


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
