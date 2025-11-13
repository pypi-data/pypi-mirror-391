from __future__ import annotations

import json
import time
from pathlib import Path
from typing import List

from ..types import Job


def _read_text_safe(path: Path) -> str:
    if not path.exists():
        return ""
    try:
        return path.read_text()
    except Exception:
        return ""


def load_jobs(path: Path | str) -> List[Job]:
    """
    Load jobs from JSON. Tolerates missing/empty/corrupt files.
    Returns a list of Job models.
    """
    p = Path(path)
    txt = _read_text_safe(p)
    if not txt.strip():
        return []
    try:
        raw = json.loads(txt)
    except Exception:
        return []
    jobs: List[Job] = []
    for item in raw if isinstance(raw, list) else []:
        try:
            # Accept both plain strings and enum values for state via model parsing
            jobs.append(Job(**item))
        except Exception:
            # Skip malformed rows
            continue
    return jobs


def save_jobs(path: Path | str, jobs: List[Job]) -> None:
    """
    Persist jobs to JSON (atomic write).
    """
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    payload = [j.to_dict() for j in jobs]
    tmp = p.with_suffix(".tmp")
    tmp.write_text(json.dumps(payload, indent=2))
    tmp.replace(p)


def upsert_job(path: Path | str, job: Job) -> None:
    """
    Insert or replace a job by id, then save.
    """
    jobs = load_jobs(path)
    found = False
    for i, j in enumerate(jobs):
        if j.id == job.id:
            job.updated_at = time.time()
            jobs[i] = job
            found = True
            break
    if not found:
        jobs.append(job)
    save_jobs(path, jobs)
