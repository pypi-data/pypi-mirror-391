from __future__ import annotations
from pathlib import Path
import shutil
import subprocess


class ISOToolError(RuntimeError): ...


def have(cmd: str) -> bool:
    return shutil.which(cmd) is not None


def check_xorriso() -> None:
    if not have("xorriso"):
        raise ISOToolError("xorriso not installed. Try: sudo apt install -y xorriso")


def build_combined_iso(os_iso: Path, seed_dir: Path, out_iso: Path) -> Path:
    """
    Create a new ISO by taking the original installer ISO (os_iso)
    and *adding* NoCloud seed files into the filesystem so cloud-init
    can find /nocloud/{user-data,meta-data} on first boot.

    Requires: xorriso
    Strategy:
      -indev <os.iso>            → open original
      -map <seed/user-data> /nocloud/user-data
      -map <seed/meta-data> /nocloud/meta-data
      -outdev <combined.iso>     → write new ISO
      -boot_image any replay     → preserve bootable settings from source

    Notes:
      * This does not modify kernel cmdline. Ubuntu autoinstall detects
        embedded NoCloud if present in the media.
      * For non-Ubuntu ISOs or changed layouts, flags might need tweaking.
    """
    check_xorriso()
    user_data = seed_dir / "user-data"
    meta_data = seed_dir / "meta-data"
    if not user_data.exists() or not meta_data.exists():
        raise ISOToolError("Seed dir missing user-data or meta-data")

    out_iso.parent.mkdir(parents=True, exist_ok=True)

    cmd = [
        "xorriso",
        "-indev",
        str(os_iso),
        "-map",
        str(user_data),
        "/nocloud/user-data",
        "-map",
        str(meta_data),
        "/nocloud/meta-data",
        "-outdev",
        str(out_iso),
        "-boot_image",
        "any",
        "replay",
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise ISOToolError(f"xorriso failed: {proc.stderr.strip()[:400]}")
    return out_iso
