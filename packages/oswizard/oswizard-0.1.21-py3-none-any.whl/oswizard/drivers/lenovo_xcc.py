# oswizard/drivers/lenovo_xcc.py
from __future__ import annotations
from .redfish import RedfishVirtualMedia


class LenovoXCC(RedfishVirtualMedia):
    """
    Lenovo XCC virtual media wrapper.
    """

    def __init__(self, machine: dict, simulate: bool = True):
        super().__init__(
            host=machine.get("host", ""),
            user=machine.get("user", ""),
            password=machine.get("password", ""),
            simulate=simulate,
        )
