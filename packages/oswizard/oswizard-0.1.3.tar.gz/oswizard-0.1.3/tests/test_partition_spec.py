from __future__ import annotations

from pathlib import Path

import oswizard.partition_spec as ps
from oswizard.render.autoinstall import render_autoinstall
from oswizard.render.cloudinit import render_cloudinit
from oswizard.render.ks import render_kickstart


def _data(name: str) -> Path:
    return Path("tests/partition_data") / name


def test_single_disk_validate_and_render():
    spec = ps.validate_spec_file(_data("single.yml"))
    ks = render_kickstart(spec)
    assert "part / --size=" in ks
    ci = render_cloudinit(spec)
    assert "/\n" in ci or "path: /" in ci
    ai = render_autoinstall(spec)
    assert "autoinstall:" in ai


def test_raid1_validate_and_render():
    spec = ps.validate_spec_file(_data("raid1.yml"))
    ks = render_kickstart(spec)
    assert "raid / --device=md0 --fstype=ext4 --level=1" in ks
    ci = render_cloudinit(spec)
    assert "raid: md0" in ci or "name: md0" in ci


def test_lvm_validate_and_render():
    spec = ps.validate_spec_file(_data("lvm.yml"))
    ks = render_kickstart(spec)
    assert "volgroup vg0" in ks
    assert "logvol / --vgname=vg0 --name=root" in ks
    ai = render_autoinstall(spec)
    assert "lvm_vg" in ai and "lvm_lv" in ai
