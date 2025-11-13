class OSWError(Exception):
    """Base error for OSWizard."""

    pass


class AuthError(OSWError):
    """BMC authentication failed (bad user/pass or locked)."""

    pass


class UnreachableError(OSWError):
    """BMC or resource not reachable (network/DNS/TLS)."""

    pass


class BadRequestError(OSWError):
    """BMC rejected the request (unsupported action/path/body)."""

    pass


class MediaMountError(OSWError):
    """Virtual media mount failed."""

    pass


class CommandError(OSWError):
    """Local command (ipmitool) failed."""

    def __init__(self, cmd: list[str], rc: int, out: str, err: str):
        self.cmd = cmd
        self.rc = rc
        self.out = out
        self.err = err
        super().__init__(f"rc={rc} cmd={' '.join(cmd)} err={err.strip()}")
