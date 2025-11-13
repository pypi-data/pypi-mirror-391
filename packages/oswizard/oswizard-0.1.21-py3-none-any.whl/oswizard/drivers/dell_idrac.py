# oswizard/drivers/dell_idrac.py
from __future__ import annotations
from .redfish import RedfishVirtualMedia


class DellIDRAC(RedfishVirtualMedia):
    """
    Dell iDRAC virtual media wrapper (inherits generic Redfish VM).
    Accepts a machines.yml dict in ctor for compatibility with orchestrator.
    """

    def __init__(self, machine: dict, simulate: bool = True):
        super().__init__(
            host=machine.get("host", ""),
            user=machine.get("user", ""),
            password=machine.get("password", ""),
            simulate=simulate,
        )
