# oswizard/drivers/ipmi.py
from __future__ import annotations

import subprocess
from dataclasses import dataclass

from ..utils.logger import log


@dataclass
class IpmiTool:
    host: str
    user: str
    password: str
    real: bool = False  # when False, only log "would run ..." and return 0

    def _cmd(self, *args: str) -> list[str]:
        base = [
            "ipmitool",
            "-I",
            "lanplus",
            "-H",
            self.host,
            "-U",
            self.user,
            "-P",
            self.password,
        ]
        return base + list(args)

    def _run(self, *args: str) -> int:
        cmd = self._cmd(*args)
        if not self.real:
            log(f"[IPMI] would run: {' '.join(cmd)}")
            return 0
        try:
            log(f"[IPMI] run: {' '.join(cmd)}")
            res = subprocess.run(cmd, capture_output=True, text=True, check=True)
            if res.stdout:
                log(f"[IPMI] stdout: {res.stdout.strip()}")
            if res.stderr:
                log(f"[IPMI] stderr: {res.stderr.strip()}")
            return res.returncode
        except subprocess.CalledProcessError as e:
            log(
                f"[IPMI] error rc={e.returncode}: {e.stderr.strip() if e.stderr else ''}"
            )
            raise

    # Public ops used by orchestrator
    def set_boot_cdrom(self, job_id: str | None = None):
        self._run("chassis", "bootdev", "cdrom", "options=efiboot")

    def power_cycle(self, job_id: str | None = None):
        self._run("chassis", "power", "cycle")
