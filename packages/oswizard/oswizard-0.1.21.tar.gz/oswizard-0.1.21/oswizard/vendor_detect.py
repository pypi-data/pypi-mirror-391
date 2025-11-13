"""
Vendor autodiscovery for OSWizard.
- Reads DMI fields from /sys/class/dmi/id/
- Falls back to dmidecode (if available)
- Adds lightweight PCI vendor sample via lspci (if available)
- Persists to JSON manifest
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any, Dict

LOG_DIR = Path("/var/log/oswizard")
MANIFEST = Path("/etc/oswizard/manifest.json")


def _read(path: Path) -> str | None:
    try:
        return path.read_text(errors="ignore").strip() or None
    except Exception:
        return None


def _cmd(args) -> str | None:
    try:
        out = subprocess.check_output(
            args, text=True, stderr=subprocess.DEVNULL, timeout=3
        )
        return out.strip() or None
    except Exception:
        return None


def probe_vendor() -> Dict[str, Any]:
    base = Path("/sys/class/dmi/id")
    vendor: Dict[str, Any] = {
        "sys_vendor": _read(base / "sys_vendor"),
        "product_name": _read(base / "product_name"),
        "product_version": _read(base / "product_version"),
        "board_vendor": _read(base / "board_vendor"),
        "board_name": _read(base / "board_name"),
        "chassis_vendor": _read(base / "chassis_vendor"),
    }

    # Fallbacks
    if not vendor["sys_vendor"]:
        dmiv = _cmd(["dmidecode", "-s", "system-manufacturer"])
        if dmiv:
            vendor["sys_vendor"] = dmiv

    if not vendor["product_name"]:
        dmin = _cmd(["dmidecode", "-s", "system-product-name"])
        if dmin:
            vendor["product_name"] = dmin

    # Light PCI sample (optional)
    lspci_line = _cmd(
        ["sh", "-lc", "command -v lspci >/dev/null 2>&1 && lspci -mm | head -n1"]
    )
    if lspci_line:
        vendor["pci_sample"] = lspci_line

    return vendor


def persist_vendor_info() -> Dict[str, Any]:
    info = {"vendor": probe_vendor()}
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    (LOG_DIR / "vendor_detect.log").write_text(
        json.dumps(info["vendor"], indent=2, sort_keys=True)
    )
    MANIFEST.write_text(json.dumps(info, indent=2, sort_keys=True))
    return info["vendor"]
