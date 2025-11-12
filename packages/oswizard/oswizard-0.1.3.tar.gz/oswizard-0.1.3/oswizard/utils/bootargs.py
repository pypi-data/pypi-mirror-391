# oswizard/utils/bootargs.py
from __future__ import annotations
from pathlib import Path
import yaml


TEMPLATES_ROOT = Path(__file__).resolve().parents[1] / "templates"


def load_meta(template: str) -> dict:
    """
    Load templates/<template>/meta.yml as a dict.
    Returns {} if file is missing or invalid YAML.
    """
    meta_path = TEMPLATES_ROOT / template / "meta.yml"
    try:
        if not meta_path.exists():
            return {}
        with meta_path.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        if not isinstance(data, dict):
            return {}
        return data
    except Exception:
        return {}


def get_boot_args(template: str, vars: dict) -> str:
    """
    Returns kernel boot args defined in meta.yml under `boot_args`.
    - If absent, returns "".
    - Supports simple Python .format(**vars) interpolation, e.g.:
        boot_args: "inst.ks=cdrom:/ks.cfg ip={ip} gw={gw}"
    If formatting fails (missing keys), falls back to the raw string.
    """
    meta = load_meta(template)
    boot_args = meta.get("boot_args", "")
    if not boot_args or not isinstance(boot_args, str):
        return ""

    try:
        return boot_args.format(**(vars or {}))
    except Exception:
        # Graceful fallback if some placeholders are missing
        return boot_args


def normalize_netvars(vars_in: dict) -> dict:
    """Ensure consistent network vars (ip, mask, prefix, gw, dns, iface) and valid string types."""
    out = dict(vars_in)
    # Normalize types: force everything to str for template safety
    for k, v in list(out.items()):
        if v is None:
            continue
        out[k] = str(v)

    # Fix prefix if it's invalid
    prefix = out.get("prefix")
    try:
        prefix_int = int(prefix)
        if not (0 <= prefix_int <= 32):
            raise ValueError
        out["prefix"] = str(prefix_int)
    except Exception:
        out["prefix"] = "auto"

    # If mask is missing, compute from prefix if possible
    if not out.get("mask") and out["prefix"].isdigit():
        bits = int(out["prefix"])
        if 0 <= bits <= 32:
            mask = ".".join(
                [str((0xFFFFFFFF << (32 - bits) >> i) & 255) for i in [24, 16, 8, 0]]
            )
            out["mask"] = mask

    return out
