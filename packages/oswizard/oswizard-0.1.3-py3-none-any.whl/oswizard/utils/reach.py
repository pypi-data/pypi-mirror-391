from __future__ import annotations
import socket
import subprocess
from pathlib import Path

from .retry import net_retry


def _tcp_connect(host: str, port: int, timeout: float = 5.0) -> None:
    """One-shot TCP connect (raises on error)."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    try:
        sock.connect((host, port))
    finally:
        sock.close()


@net_retry((TimeoutError, OSError, ConnectionError))
def wait_tcp_port(host: str, port: int, timeout: float = 5.0) -> None:
    """
    Retry TCP connect with backoff until success or exhaustion.
    Raises ConnectionError on failure to trigger orchestrator retry/handling.
    """
    try:
        _tcp_connect(host, port, timeout=timeout)
    except (socket.timeout, OSError) as e:
        raise ConnectionError(str(e))


def try_ssh_command(
    host: str,
    user: str,
    key_path: str,
    command: str = "echo OSWIZARD_READY",
    timeout: int = 10,
):
    """
    Attempt a one-off SSH command using system ssh (BatchMode).
    Returns (rc, stdout, stderr). Caller decides how to log.
    """
    kp = Path(key_path)
    if not kp.exists():
        return (127, "", f"ssh key not found at {key_path}")
    cmd = [
        "ssh",
        "-o",
        "StrictHostKeyChecking=no",
        "-o",
        "UserKnownHostsFile=/dev/null",
        "-o",
        "BatchMode=yes",
        "-i",
        str(kp),
        f"{user}@{host}",
        command,
    ]
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return (res.returncode, res.stdout, res.stderr)
    except subprocess.TimeoutExpired:
        return (124, "", f"ssh timeout after {timeout}s")
    except Exception as e:
        return (125, "", f"ssh error: {e}")
