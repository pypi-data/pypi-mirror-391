from __future__ import annotations

import json

import oswizard.vendor_detect as vd


def test_persist_vendor_info_writes_manifest(tmp_path, monkeypatch):
    # Redirect module paths to temp
    manifest = tmp_path / "manifest.json"
    log_dir = tmp_path / "log"
    monkeypatch.setattr(vd, "MANIFEST", manifest, raising=False)
    monkeypatch.setattr(vd, "LOG_DIR", log_dir, raising=False)

    # Run
    info = vd.persist_vendor_info()

    # Verify return type and file writes
    assert isinstance(info, dict)
    assert manifest.exists(), "manifest.json should be created"

    data = json.loads(manifest.read_text())
    assert "vendor" in data and isinstance(data["vendor"], dict)
