from __future__ import annotations
from .redfish import RedfishVirtualMedia


class ASRockRM(RedfishVirtualMedia):
    """
    Thin vendor shim for ASRock Rack (ASRock RM) using standard
    Redfish Virtual Media. Keep separate for future quirks.
    """

    def __init__(self, host: str, user: str, password: str, simulate: bool = True):
        super().__init__(host=host, user=user, password=password, simulate=simulate)

    @classmethod
    def from_machine(cls, m: dict, simulate: bool = True) -> "ASRockRM":
        return cls(
            host=m.get("host", ""),
            user=m.get("user", ""),
            password=m.get("password", ""),
            simulate=simulate,
        )
