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
    result = runner.invoke(main, ["version"])

    assert result.exit_code == 0
    assert "0.1.0" in result.output
