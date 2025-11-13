import subprocess
from typing import List


def run(cmd: List[str], check: bool = True) -> subprocess.CompletedProcess:
    """
    Run a shell command and capture its output.
    By default, raises an error if the command fails.
    """
    return subprocess.run(cmd, capture_output=True, text=True, check=check)
