from __future__ import annotations

import re
from typing import Optional
from requests import Session


_TOKEN_RE = re.compile(r"(?i)(csrftoken|xsrf-token|x-csrf-token|x-xsrf-token)=([^;]+)")


def harvest_csrf_from_cookies(session: Session) -> Optional[str]:
    jar = session.cookies.get_dict()
    for k, v in jar.items():
        if k.lower() in ("csrftoken", "xsrf-token", "x-csrf-token", "x-xsrf-token"):
            return v
    # Fallback: scan cookie header string
    raw = ";".join([f"{k}={v}" for k, v in jar.items()])
    m = _TOKEN_RE.search(raw)
    return m.group(2) if m else None


def attach_csrf_headers(session: Session) -> None:
    token = harvest_csrf_from_cookies(session)
    if not token:
        return
    # Common header shapes seen across IPMI/BMC consoles
    session.headers.setdefault("X-CSRF-Token", token)
    session.headers.setdefault("X-XSRF-TOKEN", token)
