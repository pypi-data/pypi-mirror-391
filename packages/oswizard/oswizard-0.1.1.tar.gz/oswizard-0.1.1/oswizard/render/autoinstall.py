from __future__ import annotations

from typing import Any, Dict, List

import yaml

from oswizard.partition_spec import NormalizedSpec


def render_autoinstall(spec: NormalizedSpec) -> str:
    """
    Minimal autoinstall storage config:
    - model disks/partitions
    - raid
    - lvm -> create-vg + logical volumes mapped to mount points
    """
    storage: Dict[str, Any] = {"config": []}
    cfg: List[Dict[str, Any]] = storage["config"]

    # Disks & partitions
    for d in spec.disks:
        cfg.append(
            {
                "type": "disk",
                "id": d["device"],
                "ptable": d.get("table", "gpt"),
                "match": {"size": "largest"},
            }
        )
        for idx, p in enumerate(d.get("partitions", []), start=1):
            pid = f"{d['device']}-part{idx}"
            cfg.append(
                {
                    "type": "partition",
                    "id": pid,
                    "device": d["device"],
                    "size": p["size"],
                }
            )
            if p["fs"] == "swap":
                cfg.append(
                    {
                        "type": "format",
                        "id": f"fs-{pid}",
                        "fstype": "swap",
                        "volume": pid,
                    }
                )
            else:
                cfg.append(
                    {
                        "type": "format",
                        "id": f"fs-{pid}",
                        "fstype": p["fs"],
                        "volume": pid,
                    }
                )
                if p.get("mount"):
                    cfg.append(
                        {
                            "type": "mount",
                            "id": f"mnt-{pid}",
                            "device": f"fs-{pid}",
                            "path": p["mount"],
                        }
                    )

    # RAID
    for r in spec.raid:
        rid = f"md-{r['name']}"
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
            {"type": "format", "id": f"fs-{rid}", "fstype": r["fs"], "volume": rid}
        )
        cfg.append(
            {
                "type": "mount",
                "id": f"mnt-{rid}",
                "device": f"fs-{rid}",
                "path": r["mount"],
            }
        )

    # LVM (simplified)
    if spec.lvm:
        for vg in spec.lvm["vgs"]:
            cfg.append(
                {
                    "type": "lvm_vg",
                    "id": vg["name"],
                    "name": vg["name"],
                    "devices": vg["pvs"],
                }
            )
        for lv in spec.lvm["lvs"]:
            lv_id = f"{lv['vg']}-{lv['name']}"
            cfg.append(
                {
                    "type": "lvm_lv",
                    "id": lv_id,
                    "name": lv["name"],
                    "vg": lv["vg"],
                    "size": lv["size"],
                }
            )
            cfg.append(
                {
                    "type": "format",
                    "id": f"fs-{lv_id}",
                    "fstype": lv["fs"],
                    "volume": lv_id,
                }
            )
            cfg.append(
                {
                    "type": "mount",
                    "id": f"mnt-{lv_id}",
                    "device": f"fs-{lv_id}",
                    "path": lv["mount"],
                }
            )

    return yaml.safe_dump(
        {"autoinstall": {"version": 1, "storage": storage}}, sort_keys=False
    )
