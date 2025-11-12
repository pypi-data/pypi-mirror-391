from __future__ import annotations
import json
import time
from pathlib import Path
import typer

try:
    from .utils.logger import log
except Exception:
    # fallback if logger import path moves
    def log(msg: str, level: str = "info") -> None:
        ts = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        print(f"[{ts}] [{level}] {msg}")


try:
    from .workspace import ws_from
except Exception:
    # tiny fallback workspace helper
    class Workspace:
        def __init__(self, root: Path):
            self.root = Path(root)
            self.networks_file = self.root / "networks.json"

    def ws_from(ws: str) -> Workspace:
        root = Path(ws)
        root.mkdir(parents=True, exist_ok=True)
        return Workspace(root)


networks_app = typer.Typer(
    add_completion=False,
    no_args_is_help=True,
    help="Manage network definitions (stored in networks.json)",
)


def _load_networks(path: Path) -> list[dict]:
    try:
        if not path.exists():
            return []
        txt = path.read_text()
        if not txt.strip():
            return []
        return json.loads(txt)
    except Exception as e:
        log(f"[warn] Failed to read {path}: {e} — starting with empty list", "info")
        return []


def _save_networks(path: Path, items: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(items, indent=2) + "\n")


@networks_app.command("list")
def networks_list(
    ws: str = typer.Option("./osw-work", "--ws", help="Workspace path"),
):
    """List networks."""
    w = ws_from(ws)
    items = _load_networks(w.networks_file)
    if not items:
        print("No networks found.")
        raise typer.Exit(0)
    for n in items:
        name = n.get("name", "?")
        cidr = n.get("cidr", "?")
        gw = n.get("gateway", "")
        dns = (
            ",".join(n.get("dns", []))
            if isinstance(n.get("dns"), list)
            else n.get("dns", "")
        )
        print(f"{name}\t{cidr}\t{gw}\t{dns}")


@networks_app.command("add")
def networks_add(
    name: str = typer.Argument(..., help="Network name (e.g., mgmt)"),
    cidr: str = typer.Option(..., "--cidr", help="CIDR (e.g., 10.0.0.0/24)"),
    gateway: str = typer.Option("", "--gateway", help="Default gateway (optional)"),
    dns: list[str] = typer.Option([], "--dns", help="DNS server(s), repeatable"),
    ws: str = typer.Option("./osw-work", "--ws", help="Workspace path"),
):
    """Add or replace a network."""
    w = ws_from(ws)
    items = _load_networks(w.networks_file)
    items = [n for n in items if n.get("name") != name]
    items.append({"name": name, "cidr": cidr, "gateway": gateway, "dns": dns})
    _save_networks(w.networks_file, items)
    log(f"Added/updated network {name}", "info")


@networks_app.command("remove")
def networks_remove(
    name: str = typer.Argument(..., help="Network name to remove"),
    ws: str = typer.Option("./osw-work", "--ws", help="Workspace path"),
):
    """Remove a network by name."""
    w = ws_from(ws)
    items = _load_networks(w.networks_file)
    before = len(items)
    items = [n for n in items if n.get("name") != name]
    _save_networks(w.networks_file, items)
    if len(items) < before:
        log(f"Removed network {name}", "info")
    else:
        log(f"Network {name} not found", "info")


@networks_app.command("show")
def networks_show(
    name: str = typer.Argument(..., help="Network name to show"),
    ws: str = typer.Option("./osw-work", "--ws", help="Workspace path"),
):
    """Show a network's JSON."""
    w = ws_from(ws)
    items = _load_networks(w.networks_file)
    for n in items:
        if n.get("name") == name:
            print(json.dumps(n, indent=2))
            raise typer.Exit(0)
    log(f"Network {name} not found", "info")
    raise typer.Exit(1)
