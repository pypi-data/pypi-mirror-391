from click.testing import CliRunner
from oswizard.cli import cli


def _help_for(args):
    return CliRunner().invoke(cli, args)


def test_execute_flag_is_documented_for_mount_iso():
    r = _help_for(["media", "mount-iso", "--help"])
    assert r.exit_code == 0
    assert "--execute" in r.output


def test_execute_flag_is_documented_for_set_bootdev():
    r = _help_for(["media", "set-bootdev", "--help"])
    assert r.exit_code == 0
    assert "--execute" in r.output


def test_execute_flag_is_documented_for_ventoy():
    r = _help_for(["media", "ventoy-mount", "--help"])
    assert r.exit_code == 0
    assert "--execute" in r.output
