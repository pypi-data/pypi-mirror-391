from __future__ import annotations
from pathlib import Path
from typing import List, Dict, Any, Union

# Optional: use PyYAML if available; otherwise fall back to a simple parser
try:
    import yaml  # type: ignore
except Exception:  # pragma: no cover
    yaml = None  # type: ignore


def _fallback_parse_yaml_list(txt: str) -> List[Dict[str, Any]]:
    """
    Ultra-simple YAML list-of-maps parser for lines like:
      - name: lab-01
        bmc_host: 10.0.0.100
        username: admin
        password: changeme
        driver: stub
    Only meant as a last resort if PyYAML isn't installed.
    """
    items: List[Dict[str, Any]] = []
    cur: Dict[str, Any] | None = None
    for raw in txt.splitlines():
        line = raw.rstrip()
        if not line or line.lstrip().startswith("#"):
            continue
        if line.lstrip().startswith("- "):
            # start new item
            if cur:
                items.append(cur)
            cur = {}
            after_dash = line.lstrip()[2:]
            if after_dash:
                if ":" in after_dash:
                    k, v = after_dash.split(":", 1)
                    cur[k.strip()] = v.strip().strip('"').strip("'")
            continue
        if cur is not None and ":" in line:
            k, v = line.split(":", 1)
            cur[k.strip()] = v.strip().strip('"').strip("'")
    if cur:
        items.append(cur)
    return items


def load_machines(path: Union[str, Path]) -> List[Dict[str, Any]]:
    p = Path(path)
    if not p.exists():
        return []
    txt = p.read_text(encoding="utf-8").strip()
    if not txt:
        return []
    # If file looks like JSON, try JSON first
    if txt.startswith("{") or txt.startswith("["):
        import json

        try:
            data = json.loads(txt)
        except Exception:
            data = None
        if isinstance(data, list):
            return data
    # Try YAML if available
    if yaml is not None:
        try:
            data = yaml.safe_load(txt)
            if isinstance(data, list):
                return data
            elif isinstance(data, dict):
                # allow a dict keyed by name
                return [
                    {"name": k, **(v if isinstance(v, dict) else {})}
                    for k, v in data.items()
                ]
        except Exception:
            import logging

            logging.getLogger(__name__).debug(
                "suppressed exception in try/except", exc_info=True
            )
    return _fallback_parse_yaml_list(txt)


def save_machines(path: Union[str, Path], items: List[Dict[str, Any]]) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    # Prefer YAML if available
    if yaml is not None:
        p.write_text(
            yaml.safe_dump(items, sort_keys=False, default_flow_style=False),
            encoding="utf-8",
        )
        return
    # Else write pretty JSON
    import json

    p.write_text(json.dumps(items, indent=2), encoding="utf-8")
