from __future__ import annotations

from pathlib import Path
from typing import Optional

# Reuse the real executor helper
from .ventoy_exec import ventoy_real_exec

RESCUE_SCRIPT = "scripts/rescue.sh"


def apply_rescue_patch(payload_dir: str, ttl_minutes: Optional[int] = None) -> None:
    """
    Trigger a rescue boot using a Ventoy-style directory payload containing:
      <payload_dir>/scripts/rescue.sh

    In CI we run "directory mode" (executor stub execs the script inside the dir).
    On hosts with the real Ventoy executor, this maps to prepare + boot flow.

    ttl_minutes: optional "time-to-live" hint for one-shot rescue sessions.
                 For now we log it; orchestration TTL cleanup happens elsewhere.
    """
    target = Path(payload_dir).resolve()
    if not target.exists():
        raise FileNotFoundError(f"Rescue payload not found: {target}")

    # Call into the existing executor path (directory-mode)
    ventoy_real_exec(
        image_or_dir=str(target),
        script_inside=RESCUE_SCRIPT,
        host_script=False,
        timeout=1800,
    )
    _maybe_log_ttl(ttl_minutes)


def apply_rescue_host_script(
    script_path: str, ttl_minutes: Optional[int] = None
) -> None:
    """
    Host-script mode: execute a rescue helper script directly on the host.
    Useful for quick local verification (stays non-breaking).
    """
    script = Path(script_path).resolve()
    if not script.exists():
        raise FileNotFoundError(f"Rescue host script not found: {script}")

    # Underlying executor supports a '--host-script' flag in our CI stub.
    ventoy_real_exec(
        image_or_dir=str(script),
        script_inside="",
        host_script=True,
        timeout=1800,
    )
    _maybe_log_ttl(ttl_minutes)


def _maybe_log_ttl(ttl_minutes: Optional[int]) -> None:
    if ttl_minutes is None:
        return
    msg = f"[rescue] TTL hint set to {ttl_minutes} minute(s) for one-shot session."
    try:
        # Keep it simple: print. Orchestrator can capture stdout.
        print(msg)
    except Exception as e:  # be explicit; avoid silent excepts
        import sys

        sys.stderr.write(f"{msg} (stderr fallback due to: {e})\n")
