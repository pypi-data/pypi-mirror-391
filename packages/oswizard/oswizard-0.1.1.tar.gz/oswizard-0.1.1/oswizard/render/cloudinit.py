from __future__ import annotations

from typing import Any, Dict, List

import yaml

from oswizard.partition_spec import NormalizedSpec


def render_cloudinit(spec: NormalizedSpec) -> str:
    """
    Emits a minimal cloud-init storage v1 config:
    - disks + partitions -> filesystems + mounts
    - raid arrays
    - lvm (vgs + lvs)
    """
    storage: Dict[str, Any] = {"version": 1, "config": []}
    cfg: List[Dict[str, Any]] = storage["config"]

    # Disks & partitions
    for d in spec.disks:
        disk_id = f"disk-{_basename(d['device'])}"
        cfg.append(
            {
                "type": "disk",
                "id": disk_id,
                "ptable": d.get("table", "gpt"),
                "match": {"device": d["device"]},
            }
        )
        for idx, p in enumerate(d.get("partitions", []), start=1):
            pid = f"part-{_basename(d['device'])}-{idx}"
            cfg.append(
                {"type": "partition", "id": pid, "device": disk_id, "size": p["size"]}
            )
            if p["fs"] == "swap":
                cfg.append(
                    {
                        "type": "format",
                        "id": f"fs-{pid}",
                        "volume": pid,
                        "fstype": "swap",
                    }
                )
            else:
                cfg.append(
                    {
                        "type": "format",
                        "id": f"fs-{pid}",
                        "volume": pid,
                        "fstype": p["fs"],
                    }
                )
                if p.get("mount"):
                    cfg.append(
                        {"type": "mount", "device": f"fs-{pid}", "path": p["mount"]}
                    )

    # RAID
    for r in spec.raid:
        rid = f"raid-{r['name']}"
        cfg.append(
            {
                "type": "raid",
                "id": rid,
                "name": r["name"],
                "raidlevel": r["level"],
                "devices": r["devices"],
            }
        )
        cfg.append(
            {"type": "format", "id": f"fs-{rid}", "volume": rid, "fstype": r["fs"]}
        )
        cfg.append({"type": "mount", "device": f"fs-{rid}", "path": r["mount"]})

    # LVM (simplified)
    if spec.lvm:
        # cloud-init v1 doesn’t model LVM deeply; represent as format+mount on mapper paths
        for lv in spec.lvm["lvs"]:
            dev = f"/dev/mapper/{lv['vg']}-{lv['name']}"
            fid = f"fs-lvm-{lv['vg']}-{lv['name']}"
            cfg.append({"type": "format", "id": fid, "volume": dev, "fstype": lv["fs"]})
            cfg.append({"type": "mount", "device": fid, "path": lv["mount"]})

    return "#cloud-config\n" + yaml.safe_dump({"storage": storage}, sort_keys=False)


def _basename(dev: str) -> str:
    return dev.strip().split("/")[-1]
