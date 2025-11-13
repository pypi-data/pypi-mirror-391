from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

from ..utils.logger import debug


@dataclass
class RedfishConfig:
    host: str
    user: Optional[str] = None
    password: Optional[str] = None
    insecure: bool = True


class RedfishVirtualMedia:
    """
    Minimal stub Redfish driver.
    All driver chatter logs at DEBUG so normal runs stay clean.
    """

    def __init__(
        self,
        host: str,
        user: str | None = None,
        password: str | None = None,
        insecure: bool = True,
    ):
        self.cfg = RedfishConfig(
            host=host, user=user, password=password, insecure=insecure
        )
        debug(
            f"[driver:redfish] init host={self.cfg.host} insecure={self.cfg.insecure}"
        )

    # Media controls
    def eject_cd(self, job_id: str | None = None) -> None:
        debug(f"[driver:redfish] eject_cd  job={job_id}")

    def insert_cd(self, image_url: str, job_id: str | None = None) -> None:
        debug(f"[driver:redfish] insert_cd  url={image_url} job={job_id}")

    def eject_usb(self, job_id: str | None = None) -> None:
        debug(f"[driver:redfish] eject_usb job={job_id}")

    def insert_usb(self, image_url: str, job_id: str | None = None) -> None:
        debug(f"[driver:redfish] insert_usb url={image_url} job={job_id}")

    # Boot & power
    def set_next_boot_virtual_media(self, job_id: str | None = None) -> None:
        debug(f"[driver:redfish] set_next_boot_virtual_media job={job_id}")

    def power_cycle(self, job_id: str | None = None) -> None:
        debug(f"[driver:redfish] power_cycle job={job_id}")
