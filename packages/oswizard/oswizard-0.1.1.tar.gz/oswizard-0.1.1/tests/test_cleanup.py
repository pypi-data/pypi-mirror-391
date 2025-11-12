from __future__ import annotations

import json
import os
import time
from pathlib import Path

import oswizard.cleanup as cl


def _mk_cfg(tmp_path: Path) -> dict:
    # Keep guard minimal so temp paths aren't blocked
    return {
        "retention_hours": 0,
        "paths": [str(tmp_path)],
        "include_globs": ["osw-*", "oswizard-*", "jobs/*", "osw-job-*"],
        "exclude_globs": [],
        "dangerous_paths_guard": ["/"],
    }


def test_sweep_removes_old_files(tmp_path, monkeypatch):
    # Point module config/log into tmp
    cfg_path = tmp_path / "cleanup.json"
    log_path = tmp_path / "cleanup.log"
    cfg = _mk_cfg(tmp_path)
    cfg_path.write_text(json.dumps(cfg))
    monkeypatch.setattr(cl, "CONFIG", cfg_path, raising=False)
    monkeypatch.setattr(cl, "LOGFILE", log_path, raising=False)

    # Create an "old" file that matches include_globs
    f = tmp_path / "osw-old-file"
    f.write_text("x")
    # Make it older than cutoff (retention_hours=0 => cutoff=now)
    old = time.time() - 10
    os.utime(f, (old, old))

    removed = cl.sweep()
    assert removed >= 1
    assert not f.exists()


def test_cleanup_job_removes_job_artifacts(tmp_path, monkeypatch):
    # Point module config/log into tmp
    cfg_path = tmp_path / "cleanup.json"
    log_path = tmp_path / "cleanup.log"
    cfg = _mk_cfg(tmp_path)
    cfg_path.write_text(json.dumps(cfg))
    monkeypatch.setattr(cl, "CONFIG", cfg_path, raising=False)
    monkeypatch.setattr(cl, "LOGFILE", log_path, raising=False)

    # Create job-scoped files/dirs
    job_id = "demo-123"
    job_dir = tmp_path / "jobs" / job_id
    job_dir.mkdir(parents=True)
    (job_dir / "tmpfile").write_text("x")
    stray = tmp_path / f"osw-{job_id}-abc"
    stray.write_text("x")

    removed = cl.cleanup_job(job_id)
    assert removed >= 1
    assert not job_dir.exists()
    assert not stray.exists()
