from __future__ import annotations
from pathlib import Path
import json
import time

# ---------- paths ----------


def job_log_dir(ws_root: Path | str) -> Path:
    d = Path(ws_root) / "logs"
    d.mkdir(parents=True, exist_ok=True)
    return d


def job_log_path(ws_root: Path | str, job_id: str) -> Path:
    return job_log_dir(ws_root) / f"{job_id}.log"


# ---------- logging ----------


def append_job_log(ws_root: Path | str, job_id: str, line: str):
    """Append a timestamped line to logs/<job>.log and echo to stdout."""
    ts = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    entry = f"[{ts}] {line}"
    p = job_log_path(ws_root, job_id)
    with p.open("a", encoding="utf-8") as f:
        f.write(entry + "\n")
    print(entry)


def read_job_log(ws_root: Path | str, job_id: str) -> str:
    p = job_log_path(ws_root, job_id)
    return p.read_text(encoding="utf-8") if p.exists() else ""


# ---------- failure summary ----------


def _jget(obj, key, default=None):
    if isinstance(obj, dict):
        return obj.get(key, default)
    return getattr(obj, key, default)


def write_fail_summary(
    ws_root: Path | str, job, reason_code: str, hint: str | None = None
):
    """Write logs/<job>.fail.json with a quick triage summary."""
    now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    summary = {
        "id": _jget(job, "id"),
        "machine": _jget(job, "machine"),
        "template": _jget(job, "template"),
        "state": _jget(job, "state"),
        "reason_code": reason_code,
        "hint": hint,
        "at": now,
    }
    p = job_log_dir(ws_root) / f"{summary['id']}.fail.json"
    p.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    append_job_log(ws_root, summary["id"], f"[fail] {reason_code}: {hint or ''}")
