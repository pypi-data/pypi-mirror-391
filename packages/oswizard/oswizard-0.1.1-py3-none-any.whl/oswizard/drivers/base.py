from dataclasses import dataclass


@dataclass
class DriverContext:
    host: str
    user: str
    password: str
    dry_run: bool = True  # default to dry-run mode so no real hardware gets touched


class Driver:
    """
    Base driver class — all hardware drivers (IPMI, iLO, iDRAC) inherit from this.
    """

    name = "base"

    def __init__(self, ctx: DriverContext):
        self.ctx = ctx

    def connect(self):
        raise NotImplementedError

    def mount_iso(self, iso_path: str):
        raise NotImplementedError

    def set_next_boot_iso(self):
        raise NotImplementedError

    def power_cycle(self):
        raise NotImplementedError
