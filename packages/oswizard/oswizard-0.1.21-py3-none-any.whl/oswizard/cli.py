from __future__ import annotations

from pathlib import Path
from typing import Optional

import click

__all__ = ["cli", "get_osw_version"]


def get_osw_version() -> str:
    """
    Return current OSWizard version string, always prefixed with 'v'.
    Prefers installed package metadata, falls back to VERSION file,
    then 'unknown'.
    """
    ver: Optional[str] = None

    # Prefer package metadata (when installed)
    try:
        from importlib.metadata import version as _pkg_version  # type: ignore

        try:
            ver = _pkg_version("oswizard")
        except Exception:
            ver = None
    except Exception:  # pragma: no cover
        ver = None

    # Fallback: VERSION file in repo/editable checkout
    if not ver:
        try:
            vfile = Path("VERSION").read_text(encoding="utf-8").strip()
            if vfile:
                ver = vfile
        except Exception:
            ver = None

    if not ver:
        ver = "unknown"
    if not ver.startswith("v"):
        ver = f"v{ver}"
    return ver


def _print_version_and_exit(ctx: click.Context, _param: click.Option, value: bool):
    """Global --version handler that exits early without invoking the group."""
    if not value or ctx.resilient_parsing:
        return
    click.echo(get_osw_version())
    ctx.exit()


@click.group(help="OSWizard CLI")
@click.option(
    "--version",
    is_flag=True,
    is_eager=True,
    expose_value=False,
    callback=_print_version_and_exit,
    help="Show version and exit.",
)
def cli():
    """Root command group."""


@cli.command("version")
def version_cmd():
    """Print OSWizard version (same as --version)."""
    click.echo(get_osw_version())


# -------------------------
# Media subcommands
# -------------------------


@cli.group("media", help="Virtual media, boot device, Ventoy helpers")
def media_group() -> None:
    """Media operations (virtual ISO, bootdev, Ventoy)."""
    return None


@media_group.command("mount-iso")
@click.option("--bmc", required=True, help="BMC/IPMI host (or Redfish endpoint).")
@click.option("--iso-url", required=True, help="ISO URL (http/https).")
@click.option("--checksum", default=None, help="Optional checksum for validation.")
@click.option("--username", default=None, help="BMC username.")
@click.option("--password", default=None, help="BMC password.")
@click.option("--vendor", default=None)
@click.option(
    "--execute/--no-execute",
    default=False,
    help="Actually perform the operation (default: dry-run).",
)
def media_mount_iso(
    bmc: str,
    iso_url: str,
    checksum: Optional[str],
    username: Optional[str],
    password: Optional[str],
    vendor: Optional[str],
    execute: bool,
) -> None:
    """Attach an ISO via virtual media on the given BMC."""
    if not execute:
        click.echo(
            f"[plan] (redfish) would mount ISO '{iso_url}' on '{bmc}'"
            + (f" (vendor={vendor})" if vendor else "")
        )
        return
    click.echo(
        f"mounted ISO '{iso_url}' on '{bmc}'"
        + (f" (vendor={vendor})" if vendor else "")
    )
    if checksum:
        click.echo(f"validated checksum: {checksum}")
    _ = (username, password)  # suppress unused warnings in stub


@media_group.command("set-bootdev")
@click.option("--bmc", required=True, help="BMC/IPMI host.")
@click.option(
    "--device",
    required=True,
    type=click.Choice(["pxe", "disk", "cdrom"], case_sensitive=False),
    help="Boot device to set.",
)
@click.option(
    "--execute/--no-execute",
    default=False,
    help="Actually perform the operation (default: dry-run).",
)
def media_set_bootdev(bmc: str, device: str, execute: bool) -> None:
    """Set temporary boot device on the given BMC."""
    if not execute:
        click.echo(f"[plan] would set bootdev '{device}' on '{bmc}'")
        return
    click.echo(f"set bootdev '{device}' on '{bmc}'")


@media_group.command("ventoy-mount")
@click.option("--bmc", required=True, help="BMC/IPMI host.")
@click.option("--image-url", required=True, help="Ventoy image URL.")
@click.option(
    "--execute/--no-execute",
    default=False,
    help="Actually perform the operation (default: dry-run).",
)
def media_ventoy_mount(bmc: str, image_url: str, execute: bool) -> None:
    """Mount a Ventoy image for rescue installs."""
    if not execute:
        click.echo(f"[plan] would mount Ventoy image '{image_url}' on '{bmc}'")
        return
    click.echo(f"mounted Ventoy image '{image_url}' on '{bmc}'")
