from __future__ import annotations

import json
from pathlib import Path
import typer

# We store machines as a JSON array in machines.yml (YAML superset).
# Example:
# [
#   {"name":"lab-01","bmc_host":"10.0.0.100","user":"admin","password":"changeme","driver":"stub"}
# ]


def _load_machines(path: Path) -> list[dict]:
    if not path.exists():
        return []
    txt = path.read_text().strip()
    if not txt:
        return []
    try:
        return json.loads(txt)
    except Exception:
        # If file has non-JSON YAML or junk, keep user safe: treat as empty instead of crashing
        return []


def _save_machines(path: Path, items: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(items, indent=2) + "\n")


machines_app = typer.Typer(add_completion=False, no_args_is_help=True)


@machines_app.command("list")
def machines_list(
    ws: str = typer.Option("./osw-work", "--ws", help="Workspace path"),
):
    """
    List known machines.
    """
    from .workspace import ws_from

    w = ws_from(ws)
    items = _load_machines(Path(w.machines_file))
    if not items:
        typer.echo("No machines found.")
        raise typer.Exit(0)
    for m in items:
        name = m.get("name", "?")
        host = m.get("bmc_host", "?")
        user = m.get("user", "?")
        driver = m.get("driver", "?")
        typer.echo(f"{name}\t{host}\t{user}\t{driver}")


@machines_app.command("add")
def machines_add(
    name: str = typer.Argument(..., help="Machine name (unique)"),
    bmc_host: str = typer.Option(..., "--bmc-host", help="BMC IP/host"),
    user: str = typer.Option("admin", "--user", help="BMC username"),
    password: str = typer.Option("changeme", "--password", help="BMC password"),
    driver: str = typer.Option("stub", "--driver", help="Driver: stub|redfish"),
    ws: str = typer.Option("./osw-work", "--ws", help="Workspace path"),
):
    """
    Add or replace a machine definition.
    """
    from .workspace import ws_from
    from .utils.logger import log

    w = ws_from(ws)
    path = Path(w.machines_file)
    items = _load_machines(path)
    # de-dup by name
    items = [m for m in items if m.get("name") != name]
    items.append(
        {
            "name": name,
            "bmc_host": bmc_host,
            "user": user,
            "password": password,
            "driver": driver,
        }
    )
    _save_machines(path, items)
    log(f"Added machine {name}", "info")


@machines_app.command("remove")
def machines_remove(
    name: str = typer.Argument(..., help="Machine name"),
    ws: str = typer.Option("./osw-work", "--ws", help="Workspace path"),
):
    """
    Remove a machine by name (no error if it doesn't exist).
    """
    from .workspace import ws_from
    from .utils.logger import log

    w = ws_from(ws)
    path = Path(w.machines_file)
    items = _load_machines(path)
    before = len(items)
    items = [m for m in items if m.get("name") != name]
    _save_machines(path, items)
    if len(items) < before:
        log(f"Removed machine {name}", "info")
    else:
        log(f"Machine {name} not found (no changes)", "info")
