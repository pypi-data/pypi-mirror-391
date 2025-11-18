"""Command-line interface for pln-search."""

import sys
import click
from pln_search import __version__
from pln_search.config import ConfigManager
from pln_search.auth import OAuth2Flow, AuthenticationError
from pln_search.api import PLNAPIClient, APIError
from pln_search.formatters import OutputFormatter


class DefaultCommandGroup(click.Group):
    """Click Group that defaults to 'search' command if no command is specified."""

    def resolve_command(self, ctx, args):
        """Resolve command, defaulting to 'search' if first arg is not a known command."""
        if not args:
            # No args, just return None and let invoke_without_command handle it
            return None, None, []

        # Check if first arg is a known command
        cmd_name = args[0]
        if cmd_name in self.commands:
            # It's a known command, let Click handle it normally
            return super().resolve_command(ctx, args)

        # Not a known command, default to 'search' and treat first arg as query
        return 'search', self.commands['search'], args


@click.group(cls=DefaultCommandGroup, invoke_without_command=True)
@click.pass_context
def main(ctx):
    """PLN Search - Search the PLN Directory API.

    Examples:
        pln-search "John Doe"                 # Global search (default)
        pln-search --members "John"           # Search members
        pln-search --teams "Protocol"         # Search teams
        pln-search search "John Doe"          # Explicit search command
        pln-search auth login                 # Show auth setup
        pln-search auth token --interactive   # Configure token
    """
    # If no subcommand was invoked, show help
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@main.command()
@click.option("--members", "search_type", flag_value="members", help="Search members only")
@click.option("--teams", "search_type", flag_value="teams", help="Search teams only")
@click.option("--projects", "search_type", flag_value="projects", help="Search projects only")
@click.option("--limit", default=20, help="Maximum results to show", type=int)
@click.option("--json", "output_json", is_flag=True, help="Output JSON")
@click.option("--no-color", is_flag=True, help="Plain text output")
@click.argument("query")
def search(search_type, limit, output_json, no_color, query):
    """Search the PLN Directory API.

    Examples:
        pln-search search "John Doe"                 # Global search
        pln-search search --members "John"           # Search members
        pln-search search --teams "Protocol"         # Search teams
        pln-search search --projects "IPFS"          # Search projects
        pln-search search "query" --json             # JSON output
    """
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


@main.command()
def version():
    """Show version information."""
    click.echo(f"pln-search version {__version__}")


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


@auth.command("token")
@click.argument("access_token", required=False)
@click.option("--interactive", "-i", is_flag=True, help="Enter token interactively")
@click.option("--refresh-token", help="Optional refresh token")
def auth_token(access_token, interactive, refresh_token):
    """Set authentication token manually.

    Usage:
        pln-search auth token <token>              # Set token from argument
        pln-search auth token --interactive        # Enter token interactively
    """
    try:
        # Interactive mode
        if interactive:
            click.echo("Paste your access token (it will be hidden):")
            access_token = click.prompt("Access Token", hide_input=True)

            if click.confirm("Do you have a refresh token?", default=False):
                refresh_token = click.prompt("Refresh Token", hide_input=True)

        # Validate we have a token
        if not access_token:
            click.echo("✗ Error: No token provided", err=True)
            click.echo("  Use: pln-search auth token <token>", err=True)
            click.echo("  Or:  pln-search auth token --interactive", err=True)
            sys.exit(1)

        # Save credentials
        config = ConfigManager()
        auth_flow = OAuth2Flow(config.get_api_base_url(), config)
        auth_flow.set_manual_credentials(access_token, refresh_token)

        click.echo("✓ Token saved successfully")
        click.echo(f"  Config: {config.get_config_dir()}/credentials.json")
        click.echo()
        click.echo("Test your authentication with: pln-search auth status")

    except Exception as e:
        click.echo(f"✗ Failed to save token: {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
