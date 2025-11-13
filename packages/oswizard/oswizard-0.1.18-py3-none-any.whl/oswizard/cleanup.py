from __future__ import annotations

import argparse
import json
import logging
import os
import shutil
import sys
import time
from pathlib import Path
from typing import List

DEFAULT_LOG = Path("/var/log/oswizard/cleanup.log")
# Allow CI/tests to override the logfile location
LOGFILE = Path(os.environ.get("OSW_CLEANUP_LOG", str(DEFAULT_LOG)))


def _build_handlers() -> list[logging.Handler]:
    handlers: list[logging.Handler] = [logging.StreamHandler(sys.stdout)]
    from contextlib import suppress

    with suppress(PermissionError, FileNotFoundError, OSError):
        if LOGFILE.is_absolute():
            LOGFILE.parent.mkdir(parents=True, exist_ok=True)
        handlers.insert(0, logging.FileHandler(LOGFILE))
    return handlers


CONFIG = Path("/etc/oswizard/cleanup.json")
LOGFILE = Path("/var/log/oswizard/cleanup.log")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [cleanup] %(levelname)s: %(message)s",
    handlers=[logging.FileHandler(LOGFILE), logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger("osw.cleanup")


def _load_cfg() -> dict:
    if CONFIG.exists():
        try:
            return json.loads(CONFIG.read_text())
        except Exception as e:
            log.warning("Failed to read %s: %s", CONFIG, e)
    return {
        "retention_hours": 24,
        "paths": ["/var/tmp/oswizard", "/tmp"],
        "include_globs": ["osw-*", "oswizard-*", "jobs/*", "osw-job-*"],
        "exclude_globs": [],
        "dangerous_paths_guard": [
            "/",
            "/root",
            "/home",
            "/etc",
            "/var",
            "/usr",
            "/bin",
            "/sbin",
            "/lib",
            "/lib64",
            "/opt",
        ],
    }


def _is_dangerous(p: Path, guard: List[str]) -> bool:
    p = p.resolve()
    for g in guard:
        try:
            if p == Path(g).resolve():
                return True
        except Exception as e:
            # Avoid empty except: log and continue
            log.debug("Guard resolve check failed for %s: %s", g, e)
    return False


def _safe_remove(path: Path) -> None:
    try:
        if path.is_dir():
            shutil.rmtree(path, ignore_errors=True)
        else:
            path.unlink(missing_ok=True)
        log.info("Removed %s", path)
    except Exception as e:
        log.error("Remove failed %s: %s", path, e)


def _mtime_older_than(path: Path, cutoff: float) -> bool:
    try:
        return path.stat().st_mtime < cutoff
    except Exception:
        return False


def sweep(now: float | None = None) -> int:
    cfg = _load_cfg()
    now = now or time.time()
    cutoff = now - (cfg.get("retention_hours", 24) * 3600)
    paths = [Path(p) for p in cfg.get("paths", [])]
    inc = cfg.get("include_globs", [])
    exc = cfg.get("exclude_globs", [])
    guard = cfg.get("dangerous_paths_guard", [])
    removed = 0

    for base in paths:
        if not base.exists():
            continue
        for pattern in inc:
            for match in base.glob(pattern):
                if any(match.match(x) for x in exc):
                    continue
                if _is_dangerous(match, guard):
                    log.warning("Skipped guarded path: %s", match)
                    continue
                if _mtime_older_than(match, cutoff):
                    _safe_remove(match)
                    removed += 1
    log.info("Sweep complete. Removed=%d", removed)
    return removed


def cleanup_job(job_id: str) -> int:
    cfg = _load_cfg()
    paths = [Path(p) for p in cfg.get("paths", [])]
    guard = cfg.get("dangerous_paths_guard", [])
    removed = 0
    for base in paths:
        if not base.exists():
            continue
        for root, dirs, files in os.walk(base, topdown=False):
            for name in dirs + files:
                if job_id in name:
                    p = Path(root) / name
                    if _is_dangerous(p, guard):
                        log.warning("Guarded skip: %s", p)
                        continue
                    _safe_remove(p)
                    removed += 1
    log.info("Per-job cleanup complete. job_id=%s removed=%d", job_id, removed)
    return removed


def _main() -> None:
    ap = argparse.ArgumentParser(description="OSWizard Cleanup")
    ap.add_argument(
        "--sweep", action="store_true", help="sweep old sessions per retention policy"
    )
    ap.add_argument("--job", help="cleanup artifacts for a specific job id")
    args = ap.parse_args()

    if args.job:
        sys.exit(0 if cleanup_job(args.job) >= 0 else 1)
    if args.sweep:
        sys.exit(0 if sweep() >= 0 else 1)
    ap.print_help()
    sys.exit(2)


if __name__ == "__main__":
    _main()
