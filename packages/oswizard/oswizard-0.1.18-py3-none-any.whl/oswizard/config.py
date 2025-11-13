from dataclasses import dataclass, field
from pathlib import Path
import os
import yaml

from .utils.logger import log
from .utils.secrets import is_encrypted, decrypt_str, load_effective_key


@dataclass
class Machine:
    name: str
    host: str
    user: str
    password: str
    driver: str = "ipmi"
    meta: dict = field(default_factory=dict)


@dataclass
class Workspace:
    root: Path
    machines_file: Path
    jobs_file: Path

    @classmethod
    def init(cls, root: Path) -> "Workspace":
        root.mkdir(parents=True, exist_ok=True)
        wf = cls(
            root=root,
            machines_file=root / "machines.yml",
            jobs_file=root / "jobs.json",
        )
        if not wf.machines_file.exists():
            wf.machines_file.write_text("[]\n")
        if not wf.jobs_file.exists():
            wf.jobs_file.write_text("[]")
        return wf


def _maybe_decrypt_passwords(machines_path: Path, items: list[dict]) -> list[dict]:
    require_key = os.getenv("OSW_REQUIRE_KEY", "0") in ("1", "true", "yes")
    any_enc = any(is_encrypted(m.get("password")) for m in items)
    key = load_effective_key(machines_path)
    if any_enc and not key:
        msg = f"Encrypted passwords present but no key found. Set OSW_KEY or place .key next to {machines_path}."
        if require_key:
            raise RuntimeError(msg)
        log(f"[warn] {msg}")

    out: list[dict] = []
    for m in items:
        m2 = dict(m)
        pwd = m2.get("password", "")
        if key and is_encrypted(pwd):
            try:
                m2["password"] = decrypt_str(key, pwd)
            except Exception as e:
                log(
                    f"[err] Failed to decrypt password for '{m2.get('name', '?')}': {e}"
                )
        out.append(m2)
    return out


def load_machines(path: Path) -> list[Machine]:
    data = yaml.safe_load(path.read_text()) or []
    if not isinstance(data, list):
        raise ValueError("machines.yml must be a YAML list of machine objects")
    data = _maybe_decrypt_passwords(path, data)
    return [Machine(**m) for m in data]


def save_machines(path: Path, machines: list[Machine]) -> None:
    yaml.safe_dump([m.__dict__ for m in machines], path.open("w"))
