from __future__ import annotations
from typing import Optional
from ..utils.logger import log


class StubVirtualMedia:
    """
    Minimal Redfish-VM stub used in dry-run.  Mirrors the methods the
    Orchestrator calls so we get nice logs without touching real BMCs.
    """

    def __init__(
        self,
        host: str,
        user: str = "",
        password: str = "",
        *,
        family: Optional[str] = None,
    ):
        self.host = host
        self.user = user
        self.password = password
        self.family = family or "generic"
        log(f"[stub-redfish] init host={self.host} family={self.family}")

    # --- virtual media: CD slot ---
    def eject_cd(self, job_id: str):
        log(f"[stub-redfish] [{job_id}] eject CD on {self.host}")

    def insert_cd(self, image_url: str, job_id: str):
        log(f"[stub-redfish] [{job_id}] insert CD → {image_url}")

    # --- virtual media: USB slot ---
    def eject_usb(self, job_id: str):
        log(f"[stub-redfish] [{job_id}] eject USB on {self.host}")

    def insert_usb(self, image_url: str, job_id: str):
        log(f"[stub-redfish] [{job_id}] insert USB → {image_url}")

    # --- boot control ---
    def set_next_boot(self, job_id: str):
        log(f"[stub-redfish] [{job_id}] set next boot to VirtualMedia")

    # --- power control ---
    def power_cycle(self, job_id: str):
        log(f"[stub-redfish] [{job_id}] power cycle (off → on)")
