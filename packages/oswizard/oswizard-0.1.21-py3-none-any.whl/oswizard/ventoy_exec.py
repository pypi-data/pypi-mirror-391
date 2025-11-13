"""
Ventoy Real Exec wrapper for OSWizard (root-level).
"""

import subprocess
from pathlib import Path
import shlex

VENTOY_EXEC = "/opt/oswizard/patches/ventoy_exec.sh"


def ventoy_real_exec(
    image_or_dir: str,
    script_inside: str,
    host_script: bool = False,
    timeout: int = 1800,
) -> None:
    target = Path(image_or_dir).resolve()
    if not target.exists():
        raise FileNotFoundError(f"Ventoy target not found: {target}")
    if not Path(VENTOY_EXEC).exists():
        raise FileNotFoundError(f"Executor not found: {VENTOY_EXEC}")

    cmd = [VENTOY_EXEC, str(target), script_inside]
    if host_script:
        cmd.append("--host-script")

    proc = subprocess.run(
        cmd, check=False, timeout=timeout, text=True, capture_output=True
    )
    if proc.returncode != 0:
        raise subprocess.CalledProcessError(
            proc.returncode, shlex.join(cmd), output=proc.stdout, stderr=proc.stderr
        )


def apply_ventoy_patch(
    image_or_dir: str, script_inside: str = "scripts/apply.sh"
) -> None:
    ventoy_real_exec(
        image_or_dir=image_or_dir, script_inside=script_inside, host_script=False
    )
