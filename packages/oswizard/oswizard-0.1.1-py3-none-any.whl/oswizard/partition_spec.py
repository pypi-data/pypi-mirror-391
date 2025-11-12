from dataclasses import dataclass
from typing import TypedDict

__all__ = ["NormalizedSpec", "PartitionSpec"]


class NormalizedSpec(TypedDict, total=False):
    """Runtime-friendly normalized partition spec for renderers/tests.
    This is intentionally loose; fields can grow without breaking callers.
    """

    layout: list[dict[str, object]]
    swap: object
    fs: str
    boot: str
    meta: dict[str, object]


@dataclass
class PartitionSpec:
    """Schema container for partition specs (LVM, RAID, plain)."""

    pass  # intentionally empty for now until extended with RAID10/LUKS fields


# ----------------------------------------------------------------------
# Partition Spec Validation (added)
# ----------------------------------------------------------------------


def _obj_view_for_renderers(d: dict):
    from types import SimpleNamespace

    # Ensure keys exist with safe defaults
    d = dict(d)  # shallow copy
    d.setdefault("disks", [])
    d.setdefault("raid", [])
    d.setdefault("lvm", {})
    return SimpleNamespace(
        disks=d["disks"],
        raid=d["raid"],
        lvm=d["lvm"],
    )


def validate_spec_file(path):  # type: ignore[override]
    """
    Load a partition_spec.* file and return an object with attributes:
      .disks (list), .raid (list), .lvm (dict)
    which the renderers expect.
    """
    from pathlib import Path
    import yaml

    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Partition spec not found: {p}")

    data = yaml.safe_load(p.read_text(encoding="utf-8")) or {}

    # Normalize keys (idempotent)
    for key, default in (("disks", []), ("raid", []), ("lvm", {})):
        data.setdefault(key, default)

    return _obj_view_for_renderers(data)
