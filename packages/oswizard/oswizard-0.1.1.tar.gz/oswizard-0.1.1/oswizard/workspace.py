from __future__ import annotations
from pathlib import Path
from dataclasses import dataclass


@dataclass
class Workspace:
    root: Path
    machines_file: Path
    jobs_file: Path

    def __init__(self, root: str | Path):
        root_path = Path(root)
        self.root = root_path
        self.machines_file = root_path / "machines.yml"
        self.jobs_file = root_path / "jobs.json"

    @property
    def tmp_dir(self) -> Path:
        return self.root / "tmp"

    @property
    def logs_dir(self) -> Path:
        return self.root / "logs"

    def ensure(self) -> "Workspace":
        # ensure directories
        self.tmp_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        # ensure files
        if not self.machines_file.exists():
            self.machines_file.write_text("", encoding="utf-8")
        if not self.jobs_file.exists():
            self.jobs_file.write_text("[]", encoding="utf-8")
        return self


def ws_from(ws_path: str | Path) -> Workspace:
    """Factory used by CLI—returns a ready-to-use workspace."""
    return Workspace(ws_path).ensure()
