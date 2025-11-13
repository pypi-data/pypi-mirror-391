from __future__ import annotations
from .redfish import RedfishVirtualMedia


class HPEiLO(RedfishVirtualMedia):
    """
    Thin vendor shim for HPE iLO that uses standard Redfish Virtual Media endpoints.
    We keep a separate class in case we need HPE-specific quirks later.
    """

    def __init__(self, host: str, user: str, password: str, simulate: bool = True):
        super().__init__(host=host, user=user, password=password, simulate=simulate)

    @classmethod
    def from_machine(cls, m: dict, simulate: bool = True) -> "HPEiLO":
        return cls(
            host=m.get("host", ""),
            user=m.get("user", ""),
            password=m.get("password", ""),
            simulate=simulate,
        )
