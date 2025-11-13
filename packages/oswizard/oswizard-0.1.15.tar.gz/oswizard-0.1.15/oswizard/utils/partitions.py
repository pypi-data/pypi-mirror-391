from __future__ import annotations
from typing import List, Optional, Any
import json
import yaml
import pathlib
from pydantic import BaseModel, validator


class PartitionSpec(BaseModel):
    mount: Optional[str] = None  # e.g. "/", "/boot", "/var"
    size: Optional[str] = None  # e.g. "20G", "100%"
    fstype: Optional[str] = "ext4"
    type: Optional[str] = "primary"  # primary / logical
    boot: bool = False


class DiskSpec(BaseModel):
    device: str  # e.g. "/dev/sda"
    wipe: bool = False
    partitions: List[PartitionSpec]

    @validator("device")
    def device_must_not_be_empty(cls, v):
        if not v:
            raise ValueError("disk device cannot be empty")
        return v


class RaidSpec(BaseModel):
    name: str  # e.g. "md0"
    level: int  # 0,1,5,6,10
    devices: List[str]  # e.g. ["/dev/sda1","/dev/sdb1"]
    metadata: Optional[str] = "1.0"
    mkfs: Optional[str] = "ext4"
    mount: Optional[str] = None


def _load_text_or_file(val: str) -> str:
    if isinstance(val, str) and val.startswith("@"):
        p = pathlib.Path(val[1:])
        return p.read_text()
    return val


def parse_partition_input(raw: Any) -> List[DiskSpec]:
    if raw is None:
        return []
    if isinstance(raw, str):
        if raw.strip().lower() == "auto":
            return []
        text = _load_text_or_file(raw)
        try:
            data = json.loads(text)
        except Exception:
            data = yaml.safe_load(text)
    else:
        data = raw

    if isinstance(data, dict):
        data = [data]
    if not isinstance(data, list):
        raise ValueError("partition spec must be a list or dict")

    disks = []
    for d in data:
        disks.append(DiskSpec.parse_obj(d))
    return disks


def parse_raid_input(raw: Any) -> List[RaidSpec]:
    if raw is None:
        return []
    if isinstance(raw, str) and raw.startswith("@"):
        raw = pathlib.Path(raw[1:]).read_text()
    if isinstance(raw, str):
        try:
            data = json.loads(raw)
        except Exception:
            data = yaml.safe_load(raw)
    else:
        data = raw
    if isinstance(data, dict):
        data = [data]
    return [RaidSpec.parse_obj(x) for x in data]
