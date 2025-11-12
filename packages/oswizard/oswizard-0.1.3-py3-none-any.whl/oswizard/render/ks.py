from __future__ import annotations

from typing import List

from oswizard.partition_spec import NormalizedSpec


def render_kickstart(spec: NormalizedSpec) -> str:
    """
    Very small subset of Kickstart syntax that covers:
    - basic partitions on a single disk
    - raid1 md devices
    - simple LVM (one VG, 1+ LVs)
    """
    lines: List[str] = [
        "clearpart --all --initlabel",
        "zerombr",
    ]

    # Basic partitions
    for d in spec.disks:
        dev = d["device"]
        for p in d.get("partitions", []):
            mount = p.get("mount")
            size = p["size"]
            fs = p["fs"]
            if fs == "swap" or mount == "swap":
                lines.append(
                    f"part swap --size={_as_mb(size)} --fstype=swap --ondisk={dev}"
                )
            else:
                mnt = "/" if mount in ("/", None) and fs != "swap" else mount
                lines.append(
                    f"part {mnt} --size={_as_mb(size)} --fstype={fs} --ondisk={dev}"
                )

    # RAID1 (md) – treat all as raid if provided
    for r in spec.raid:
        name = r["name"]
        level = r["level"]
        fs = r["fs"]
        mount = r["mount"]
        devs = " ".join(r["devices"])
        lines.append(
            f"raid {mount} --device={name} --fstype={fs} --level={level} {devs}"
        )

    # LVM
    if spec.lvm:
        for vg in spec.lvm["vgs"]:
            vgname = vg["name"]
            pvs = " ".join(vg["pvs"])
            lines.append(f"volgroup {vgname} {pvs}")
        for lv in spec.lvm["lvs"]:
            vg = lv["vg"]
            name = lv["name"]
            fs = lv["fs"]
            mount = lv["mount"]
            size = _as_mb(lv["size"])
            lines.append(
                f"logvol {mount} --vgname={vg} --name={name} --fstype={fs} --size={size}"
            )

    return "\n".join(lines) + "\n"


def _as_mb(sz: str) -> int:
    s = sz.strip().lower()
    if s.endswith("g"):
        return int(float(s[:-1]) * 1024)
    if s.endswith("m"):
        return int(float(s[:-1]))
    return int(s)
