from __future__ import annotations
from pathlib import Path
from typing import Optional
import urllib.request
import shutil


def download_to(url: str, dest: str | Path, chunk_size: int = 8 * 1024 * 1024) -> bool:
    """
    Stream-download URL to dest path. Returns True on success.
    """
    dest = Path(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_suffix(dest.suffix + ".part")
    try:
        with urllib.request.urlopen(url) as r, open(tmp, "wb") as f:
            while True:
                chunk = r.read(chunk_size)
                if not chunk:
                    break
                f.write(chunk)
        tmp.rename(dest)
        return True
    except Exception:
        try:
            if tmp.exists():
                tmp.unlink()
        except Exception:
            import logging

            logging.getLogger(__name__).debug(
                "suppressed exception in try/except", exc_info=True
            )
        return False


def ensure_local_iso(os_url_or_path: str, out_path: str | Path) -> Optional[str]:
    """
    Given an http(s) URL or local path, ensure we have a local ISO at out_path.
    Returns the final local path string if available, else None.
    """
    out_path = Path(out_path)
    if os_url_or_path.startswith(("http://", "https://")):
        ok = download_to(os_url_or_path, out_path)
        return str(out_path) if ok else None
    else:
        p = Path(os_url_or_path)
        if p.exists():
            if str(p.resolve()) == str(out_path.resolve()):
                return str(out_path)
            # copy locally next to seed for serving
            try:
                shutil.copyfile(str(p), str(out_path))
                return str(out_path)
            except Exception:
                return None
        return None
