from click.testing import CliRunner
from oswizard.cli import cli


def test_media_help_lists_subcommands():
    r = CliRunner().invoke(cli, ["media", "--help"])
    assert r.exit_code == 0
    assert "mount-iso" in r.output
    assert "set-bootdev" in r.output
    assert "ventoy-mount" in r.output


def test_mount_iso_dry_run_plan():
    r = CliRunner().invoke(
        cli,
        [
            "media",
            "mount-iso",
            "--bmc",
            "idrac-10.0.0.5",
            "--iso-url",
            "https://example.com/rescue.iso",
        ],
    )
    assert r.exit_code == 0
    assert "[plan]" in r.output
    assert "redfish" in r.output.lower()
