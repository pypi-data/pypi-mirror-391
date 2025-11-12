from __future__ import annotations
import ipaddress


def cidr_to_parts(cidr: str) -> tuple[str, int, str]:
    """
    Accepts '10.0.0.61/24' or '10.0.0.61 24' or just '24' (prefix).
    Returns (ip, prefix, netmask). If ip is absent, returns ('', prefix, netmask).
    """
    if not cidr:
        return ("", 0, "")
    s = str(cidr).strip()
    ip = ""
    if "/" in s:
        ip, pref = s.split("/", 1)
    elif " " in s:
        # "10.0.0.61 24"
        ip, pref = s.split(None, 1)
    else:
        # "24" only
        pref = s
    prefix = int(pref)
    net = ipaddress.IPv4Network(f"0.0.0.0/{prefix}")
    mask = str(net.netmask)
    return (ip.strip(), prefix, mask)


def normalize_net_vars(vars_dict: dict) -> dict:
    """
    Reads common keys from vars: ip, cidr, mask, prefix, gw, dns.
    Fills missing mask/prefix from cidr, and returns a normalized dict.
    """
    out = dict(vars_dict or {})
    ip = out.get("ip") or out.get("target_ip") or ""
    cidr = out.get("cidr", "")
    mask = out.get("mask", "")
    prefix = out.get("prefix", "")
    if cidr and (not mask or not prefix):
        ip2, pref, m = cidr_to_parts(cidr)
        if ip == "" and ip2:
            ip = ip2
        if not mask:
            out["mask"] = m
        if not prefix:
            out["prefix"] = pref
        out["ip"] = ip
    return out
