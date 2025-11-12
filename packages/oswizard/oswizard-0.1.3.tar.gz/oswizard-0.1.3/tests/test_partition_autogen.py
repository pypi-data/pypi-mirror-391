from __future__ import annotations

from pathlib import Path
import yaml
import pytest

import oswizard.orchestrator as orch  # type: ignore[attr-defined]

MIN_SPEC = {
    "disk": "/dev/sda",
    "layout": [
        {"mount": "swap", "size": "2G"},
        {"mount": "/", "size": "100%"},
    ],
    "filesystem": "ext4",
}


@pytest.mark.skipif(
    not hasattr(orch, "_convert_partition_spec"),
    reason="orchestrator lacks _convert_partition_spec helper in this build",
)
def test_orchestrator_autogen_minimal(tmp_path: Path):
    spec_path = tmp_path / "partition_spec.yaml"
    spec_path.write_text(yaml.safe_dump(MIN_SPEC), encoding="utf-8")

    out = orch._convert_partition_spec(spec_path)  # type: ignore[attr-defined]

    keys = {"cloudinit", "kickstart", "autoinstall"}
    if isinstance(out, dict):
        assert keys.issubset(out.keys())
        assert all(out[k].strip() for k in keys)
    else:
        # Fallback: assert file artifacts exist next to the spec
        ci_f = spec_path.with_name("cloud-disk.yaml")
        ks_f = spec_path.with_name("ks-part.cfg")
        ai_f = spec_path.with_name("autoinstall-user-data.yaml")
        for f in (ci_f, ks_f, ai_f):
            assert f.exists() and f.read_text(encoding="utf-8").strip()
