from click.testing import CliRunner
from oswizard.cli import cli


def test_cli_help_shows_commands():
    res = CliRunner().invoke(cli, ["--help"])
    assert res.exit_code == 0
    assert "OSWizard CLI" in res.output
    assert "version" in res.output


def test_cli_version_command():
    res = CliRunner().invoke(cli, ["version"])
    assert res.exit_code == 0
    assert res.output.strip()  # prints version string
