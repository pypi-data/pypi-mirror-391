from enum import Enum
from pydantic import BaseModel, Field, field_validator, field_serializer
from typing import Any, Dict, List, Optional
import time


class JobState(str, Enum):
    QUEUED = "QUEUED"
    PREPARE = "PREPARE"
    MOUNT = "MOUNT"
    BOOT = "BOOT"
    INSTALLING = "INSTALLING"
    POSTCHECK = "POSTCHECK"
    COMPLETE = "COMPLETE"
    FAILED = "FAILED"


class Job(BaseModel):
    id: str
    machine: str
    template: str
    state: JobState = JobState.QUEUED
    vars: Dict[str, Any] = Field(default_factory=dict)
    logs: List[str] = Field(default_factory=list)
    attempts: Dict[str, int] = Field(default_factory=dict)
    reason_code: Optional[str] = None
    hint: Optional[str] = None
    created_at: float = Field(default_factory=time.time)
    updated_at: float = Field(default_factory=time.time)

    def append_log(self, message: str) -> None:
        """Append a log line and update timestamp."""
        self.logs.append(message)
        self.updated_at = time.time()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to plain dict for JSON dumps."""
        return self.model_dump()

    @field_validator("state", mode="before")
    @classmethod
    def _coerce_state(cls, v):
        # Accept JobState or strings like 'PREPARE' or 'JobState.PREPARE'
        try:
            from oswizard.types import JobState as _JobState  # type: ignore
        except Exception:
            _JobState = globals().get("JobState")
        if isinstance(v, _JobState):
            return v
        if isinstance(v, str):
            key = v.split(".")[-1].upper()
            return getattr(_JobState, key, getattr(_JobState, "QUEUED"))
        return getattr(_JobState, "QUEUED")

    @field_serializer("state")
    def _serialize_state(self, v, _info):
        # Emit plain enum name for stable logs/JSON
        return getattr(v, "name", str(v))
