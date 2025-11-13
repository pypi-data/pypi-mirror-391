# oswizard/utils/netparse.py

from __future__ import annotations
import ipaddress
from typing import Tuple


def cidr_to_mask(prefix: str | int) -> str:
    """
    Convert CIDR prefix -> dotted mask. Returns "" if invalid.
    """
    try:
        n = int(str(prefix).strip())
        if not (0 <= n <= 32):
            return ""
        mask_int = (0xFFFFFFFF << (32 - n)) & 0xFFFFFFFF if n > 0 else 0
        return ".".join(str((mask_int >> (8 * i)) & 0xFF) for i in (3, 2, 1, 0))
    except Exception:
        return ""


def mask_to_prefix(mask: str) -> int:
    """
    Convert dotted mask -> CIDR prefix. Returns -1 if invalid.
    """
    try:
        ip = ipaddress.IPv4Network(f"0.0.0.0/{mask}", strict=False)
        return ip.prefixlen
    except Exception:
        return -1


def parse_cidr(cidr: str) -> Tuple[str, str, int]:
    """
    Parse 'ip/prefix' -> (ip, dotted_mask, prefixInt).
    On error, returns ("", "", -1).
    """
    try:
        net = ipaddress.IPv4Interface(cidr.strip())
        ip = str(net.ip)
        pref = int(net.network.prefixlen)
        dotted = cidr_to_mask(pref)
        return ip, dotted, pref
    except Exception:
        return "", "", -1


def normalize_netvars(v: dict) -> dict:
    """
    Return a NEW dict with consistent, string-typed networking keys for templating:
      - ip      (str)
      - mask    (dotted decimal str)
      - prefix  (CIDR as string, e.g. "24"; "" if unknown)
      - gw, dns, iface (str)

    Accepts either:
      - cidr="10.0.0.5/24"
      - or individual ip/mask/prefix
    """
    out = dict(v or {})

    # 1) If cidr provided, parse and seed values
    cidr = str(out.get("cidr", "")).strip()
    if cidr and "/" in cidr:
        ip, dotted, pref = parse_cidr(cidr)
        if ip:
            out.setdefault("ip", ip)
        if dotted:
            out["mask"] = dotted
        if pref >= 0:
            out["prefix"] = str(pref)

    # 2) If mask present but no prefix, derive prefix
    if "mask" in out and "prefix" not in out:
        p = mask_to_prefix(str(out.get("mask", "")).strip())
        if p >= 0:
            out["prefix"] = str(p)

    # 3) If prefix present but no mask, derive mask
    if "prefix" in out and "mask" not in out:
        out["mask"] = cidr_to_mask(out.get("prefix", ""))

    # 4) Defaults
    out.setdefault("ip", "")
    out.setdefault("mask", "")
    out.setdefault("prefix", "")
    out.setdefault("gw", "")
    out.setdefault("dns", out.get("nameservers", ""))
    out.setdefault("iface", out.get("interface", ""))

    # 5) Normalize everything to strings (Pydantic likes consistent types)
    norm = {}
    for k, val in out.items():
        if val is None:
            norm[k] = ""
            continue
        sval = str(val).strip()
        if k == "prefix":
            try:
                n = int(sval)
                if 0 <= n <= 32:
                    sval = str(n)
                else:
                    sval = ""
            except Exception:
                # If it wasn't a clean int, blank it
                if sval and sval.isdigit():
                    sval = ""
                else:
                    sval = ""
        norm[k] = sval

    # 6) If mask still missing but prefix valid, derive mask
    if not norm.get("mask") and norm.get("prefix", "").isdigit():
        n = int(norm["prefix"])
        mask_int = (0xFFFFFFFF << (32 - n)) & 0xFFFFFFFF if n > 0 else 0
        norm["mask"] = ".".join(str((mask_int >> (8 * i)) & 0xFF) for i in (3, 2, 1, 0))

    return norm
