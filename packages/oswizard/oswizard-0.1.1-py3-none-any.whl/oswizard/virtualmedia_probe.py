from __future__ import annotations

from typing import List, Tuple
import requests


CANDIDATES = [
    "/redfish/v1/Managers/1/VirtualMedia",
    "/redfish/v1/Managers/Self/VirtualMedia",
    "/redfish/v1/Managers/Manager.Embedded.1/VirtualMedia",
]


def probe_virtualmedia_slots(
    base_url: str, session: requests.Session
) -> List[Tuple[str, int]]:
    """
    Return list of (href, count) candidate collections discovered, without raising.
    """
    found = []
    for path in CANDIDATES:
        url = base_url.rstrip("/") + path
        try:
            r = session.get(url, timeout=10)
            if r.ok and isinstance(r.json(), dict):
                j = r.json()
                members = j.get("Members") or j.get("members") or []
                found.append((path, len(members)))
        except Exception:
            # non-fatal probe
            continue
    return found
