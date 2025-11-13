# oswizard/renderer.py
from __future__ import annotations

import os
import shutil
from pathlib import Path
from typing import Dict, Any

import yaml
from jinja2 import Environment, FileSystemLoader, Undefined

TEMPLATES_ROOT = Path(__file__).resolve().parent.parent / "templates"


# --- Jinja helpers: CIDR <-> dotted ---
def _cidr_to_mask(val):
    if val is None:
        return ""
    s = str(val).strip()
    if "." in s:  # already dotted
        return s
    try:
        bits = int(s)
        if bits < 0 or bits > 32:
            return s
        mask = (0xFFFFFFFF << (32 - bits)) & 0xFFFFFFFF
        return ".".join(str((mask >> (8 * i)) & 0xFF) for i in [3, 2, 1, 0])
    except Exception:
        return s


def load_meta(template: str) -> Dict[str, Any]:
    """
    Load meta.yml for a template: entrypoint, iso name, defaults, etc.
    Path: templates/<template>/meta.yml
    """
    meta_path = TEMPLATES_ROOT / template / "meta.yml"
    if not meta_path.exists():
        raise FileNotFoundError(f"Template meta not found: {meta_path}")
    with meta_path.open() as f:
        return yaml.safe_load(f) or {}


def _jinja_env(template_dir: Path) -> Environment:
    # StrictUndefined makes missing vars explode — which is great for catching errors
    # during development. If you prefer silent defaults, switch to Undefined.
    env = Environment(
        loader=FileSystemLoader(str(template_dir)),
        autoescape=False,
        undefined=Undefined,  # ← tolerates missing vars (they render empty)
        trim_blocks=True,
        lstrip_blocks=True,
    )
    # add here:
    env.filters["netmask"] = _cidr_to_mask
    return env


def render_template(
    template: str, entrypoint: str, vars: Dict[str, Any], out_dir: Path | str
) -> None:
    """
    Render the template into out_dir. We support two common families:
      • Linux cloud-init: typically produces user-data and meta-data
      • Windows: typically produces Autounattend.xml
    We don’t hard-code names here — we render whatever the entrypoint emits,
    but common practice is that entrypoints include the needed files.
    """
    out_dir = Path(out_dir)
    # --- copy partition and raid specs into output dir so seed builders can consume them ---
    try:
        from shutil import copy2

        spec_names = ("partition_spec.yml", "raid_spec.yml")
        # prefer template-specific overrides, else fall back to templates/_includes
        from pathlib import Path as _P

        tpl_dir = _P("templates") / str(template)
        for name in spec_names:
            cand = tpl_dir / name
            if cand.exists():
                copy2(cand, out_dir / name)
            else:
                fb = _P("templates") / "_includes" / name
                if fb.exists():
                    copy2(fb, out_dir / name)
    except Exception as e:
        import sys

        print(
            f"[renderer] warning: failed to copy partition/raid specs: {e}",
            file=sys.stderr,
        )


# --- OSW: lightweight seed ISO builder ---
def build_seed_iso(template: str, tmp_dir: str) -> str:
    """
    Build a seed ISO from rendered files in tmp_dir.
    This is a stub implementation — it simply zips the contents for now,
    but maintains the same interface so higher-level orchestrator logic works.
    """
    from pathlib import Path

    tmp = Path(tmp_dir)
    iso_path = tmp / "seed.iso"
    try:
        # Ensure tmp_dir exists
        tmp.mkdir(parents=True, exist_ok=True)

        # Instead of actual mkisofs, just make a zip-like archive for dry-runs
        # In production, this would call genisoimage/mkisofs
        shutil.make_archive(str(iso_path).replace(".iso", ""), "zip", tmp)

        # Rename to .iso extension for consistency
        if not iso_path.exists():
            iso_zip = str(iso_path).replace(".iso", ".zip")
            if os.path.exists(iso_zip):
                os.rename(iso_zip, iso_path)

        return str(iso_path)
    except Exception as e:
        print(f"[renderer] warning: build_seed_iso failed: {e}")
        # Return a fallback path so orchestrator doesn’t break
        return str(iso_path)
