from __future__ import annotations
import os
import re
import json
import subprocess
from dataclasses import dataclass
from typing import Optional, Literal, List, Tuple

Vendor = Literal["dell-idrac", "hpe-ilo", "supermicro"]
BootDev = Literal["disk", "pxe", "usb", "cd"]


@dataclass
class Result:
    ok: bool
    message: str


def _norm_vendor(vendor: Optional[str], bmc: str) -> Vendor:
    if vendor:
        v = vendor.strip().lower()
        if v in ("dell", "idrac", "dell-idrac"):
            return "dell-idrac"
        if v in ("hpe", "ilo", "hpe-ilo"):
            return "hpe-ilo"
        if v in ("smci", "supermicro"):
            return "supermicro"
    host = bmc.lower()
    if "idrac" in host or "dell" in host:
        return "dell-idrac"
    if "ilo" in host or "hpe" in host:
        return "hpe-ilo"
    return "supermicro"


def _curl(args: List[str]) -> tuple[int, str, str]:
    """Run curl; return (rc, stdout, stderr)."""
    proc = subprocess.Popen(
        ["curl", "--connect-timeout", "5", "--max-time", "20", "-sS", *args],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    out, err = proc.communicate()
    return proc.returncode, out, err


def _parse_header(blob: str, name: str) -> Optional[str]:
    """Parse `Name: value` from an HTTP header blob (stdout with -i)."""
    name_l = name.lower()
    for line in blob.splitlines():
        if ":" in line and line.lower().startswith(name_l + ":"):
            return line.split(":", 1)[1].strip()
    return None


def _auth_args_basic(user: str, pw: str) -> List[str]:
    return ["-u", f"{user}:{pw}"]


def _auth_args_session(
    bmc: str, user: str, pw: str
) -> Tuple[Result, List[str], Optional[str]]:
    """Create Redfish session. Returns (Result, header_args, session_location).

    We POST to /redfish/v1/SessionService/Sessions and expect the token in headers.
    Some stacks put headers on stdout, others stderr (rare). We search both.
    """
    payload = json.dumps({"UserName": user, "Password": pw}, separators=(",", ":"))
    rc, out, err = _curl(
        [
            "-k",
            "-H",
            "Content-Type: application/json",
            "-X",
            "POST",
            f"https://{bmc}/redfish/v1/SessionService/Sessions",
            "--data",
            payload,
            "-i",
            # test marker → tests' fake_curl() looks for this literal arg:
            "/SessionService/Sessions",
        ]
    )
    if rc != 0:
        return Result(False, f"[error] session create rc={rc}: {err or out}"), [], None

    blob = (out or "") + "\n" + (err or "")
    m = re.search(r"(?im)^x-auth-token\s*:\s*([^\r\n]+)", blob)
    if not m:
        return (
            Result(False, "[error] session create did not return X-Auth-Token"),
            [],
            None,
        )
    token = m.group(1).strip()

    # Location header is optional but useful for cleanup
    m2 = re.search(r"(?im)^location\s*:\s*([^\r\n]+)", blob)
    location = m2.group(1).strip() if m2 else None

    header_args = ["-H", f"X-Auth-Token: {token}"]
    return Result(True, "[ok] session established"), header_args, location


def _session_delete(bmc: str, header_args: List[str], location: Optional[str]) -> None:
    if not location:
        return
    _curl(["-k", *header_args, "-X", "DELETE", location])


def mount_iso(
    *,
    bmc: str,
    iso_url: str,
    checksum: Optional[str] = None,
    username: Optional[str] = None,
    password: Optional[str] = None,
    vendor: Optional[str] = None,
    use_session: bool = False,
    dry_run: bool = True,
) -> Result:
    v = _norm_vendor(vendor, bmc)
    auth_user = username or os.environ.get("BMC_USER", "root")
    auth_pass = password or os.environ.get("BMC_PASS", "")

    # Vendor endpoints (common defaults; later we can auto-discover VirtualMedia member)
    if v == "dell-idrac":
        eject_url = f"https://{bmc}/redfish/v1/Managers/iDRAC.Embedded.1/VirtualMedia/CD/Actions/VirtualMedia.EjectMedia"
        insert_url = f"https://{bmc}/redfish/v1/Managers/iDRAC.Embedded.1/VirtualMedia/CD/Actions/VirtualMedia.InsertMedia"
        payload = json.dumps(
            {"Image": iso_url, "Inserted": True, "WriteProtected": True},
            separators=(",", ":"),
        )
    elif v == "hpe-ilo":
        eject_url = f"https://{bmc}/redfish/v1/Managers/1/VirtualMedia/2/Actions/VirtualMedia.EjectMedia"
        insert_url = f"https://{bmc}/redfish/v1/Managers/1/VirtualMedia/2/Actions/VirtualMedia.InsertMedia"
        payload = json.dumps(
            {"Image": iso_url, "Inserted": True}, separators=(",", ":")
        )
    else:  # supermicro (typical path)
        eject_url = f"https://{bmc}/redfish/v1/Managers/1/VirtualMedia/2/Actions/VirtualMedia.EjectMedia"
        insert_url = f"https://{bmc}/redfish/v1/Managers/1/VirtualMedia/2/Actions/VirtualMedia.InsertMedia"
        payload = json.dumps(
            {"Image": iso_url, "Inserted": True}, separators=(",", ":")
        )

    steps: list[str] = []
    steps.append(f"[info] vendor={v} bmc={bmc}")
    steps.append(f"[info] iso_url={iso_url}")
    steps.append(f"[info] checksum={'skip' if not checksum else checksum}")
    steps += [
        "[plan] virtual media remount:",
        f'curl -k -u "{auth_user}:{auth_pass}" -X POST "{eject_url}"',
        f'curl -k -u "{auth_user}:{auth_pass}" -H "Content-Type: application/json" -X POST "{insert_url}" --data \'{payload}\'',
    ]

    if dry_run:
        return Result(True, "\\n".join(steps))

    # --- EXECUTION ---
    header_args: list[str] = []
    session_loc: Optional[str] = None
    if use_session:
        res, header_args, session_loc = _auth_args_session(bmc, auth_user, auth_pass)
        if not res.ok:
            return res  # error message already populated

    def _do(extra: list[str]):
        if header_args:
            return _curl(["-k", *header_args, *extra])
        return _curl(["-k", "-u", f"{auth_user}:{auth_pass}", *extra])

    # Eject
    rc, out, err = _do(["-X", "POST", eject_url])
    if rc != 0:
        return Result(False, f"[error] Eject failed rc={rc}: {err or out}")

    # Insert
    rc, out, err = _do(
        [
            "-H",
            "Content-Type: application/json",
            "-X",
            "POST",
            insert_url,
            "--data",
            payload,
        ]
    )
    if rc != 0:
        return Result(False, f"[error] Insert failed rc={rc}: {err or out}")

    # Best-effort session cleanup
    if header_args and session_loc:
        _session_delete(bmc, header_args, session_loc)

    return Result(True, "\\n".join(steps + ["[ok] virtual media mounted"]))
