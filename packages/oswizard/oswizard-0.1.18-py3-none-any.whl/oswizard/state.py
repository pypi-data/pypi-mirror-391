# oswizard/state.py
from __future__ import annotations
import time
from typing import Any, Dict, List
from pydantic import BaseModel, Field, model_validator


class JobState:
    QUEUED = "QUEUED"
    PREPARE = "PREPARE"
    MOUNT = "MOUNT"
    BOOT = "BOOT"
    INSTALLING = "INSTALLING"
    POSTCHECK = "POSTCHECK"
    COMPLETE = "COMPLETE"
    FAILED = "FAILED"


def new_job_id() -> str:
    import secrets

    return secrets.token_hex(6)


class Job(BaseModel):
    id: str
    machine: str
    template: str
    state: str = Field(default=JobState.QUEUED)
    # Allow any input types, we’ll normalize to strings in the validator:
    vars: Dict[str, Any] = Field(default_factory=dict)
    logs: List[str] = Field(default_factory=list)
    attempts: Dict[str, int] = Field(default_factory=dict)
    reason_code: str | None = None
    hint: str | None = None
    created_at: float = Field(default_factory=time.time)
    updated_at: float = Field(default_factory=time.time)

    @model_validator(mode="before")
    def _coerce_vars_to_strings(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ensure vars is a dict of strings: str(value) for all values,
        and map None -> "" so Pydantic never sees ints/bools here.
        """
        v = dict((data.get("vars") or {}))
        sv: Dict[str, str] = {}
        for k, val in v.items():
            if val is None:
                sv[k] = ""
            else:
                sv[k] = str(val).strip()
        data["vars"] = sv
        return data


def load_jobs(path):
    import json
    import os

    if not os.path.exists(path):
        return []
    data = json.load(open(path))
    return [Job(**j) for j in data]


def save_jobs(path, jobs: list[Job]):
    import json

    json.dump([j.dict() for j in jobs], open(path, "w"))


def stamp_failure(job: Job, code: str, hint: str):
    job.state = JobState.FAILED
    job.reason_code = code
    job.hint = hint
    job.updated_at = time.time()
