from pathlib import Path
import shutil
import subprocess


def build_seed_iso(work_dir: Path, out_iso: Path) -> Path:
    """
    Build a NoCloud seed ISO from user-data + meta-data in work_dir.
    Tries xorriso first, falls back to genisoimage.
    The volume label must be 'cidata' for cloud-init NoCloud.
    """
    user = work_dir / "user-data"
    meta = work_dir / "meta-data"
    if not user.exists() or not meta.exists():
        raise FileNotFoundError("user-data or meta-data missing in " + str(work_dir))

    out_iso.parent.mkdir(parents=True, exist_ok=True)

    # Prefer xorriso (more universal), fallback to genisoimage
    if shutil.which("xorriso"):
        cmd = [
            "xorriso",
            "-as",
            "mkisofs",
            "-volid",
            "cidata",
            "-joliet",
            "-rock",
            "-o",
            str(out_iso),
            str(user),
            str(meta),
        ]
    elif shutil.which("genisoimage"):
        cmd = [
            "genisoimage",
            "-volid",
            "cidata",
            "-joliet",
            "-rock",
            "-output",
            str(out_iso),
            str(user),
            str(meta),
        ]
    else:
        raise RuntimeError("Neither xorriso nor genisoimage is installed")

    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(f"ISO build failed: {proc.stderr.strip()}")

    return out_iso
