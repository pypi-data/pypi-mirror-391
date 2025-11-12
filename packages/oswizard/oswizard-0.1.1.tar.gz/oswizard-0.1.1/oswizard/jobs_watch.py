import argparse
import json
import sys
import time
from pathlib import Path

TERMINAL_STATES = {"COMPLETE", "FAILED"}


def _latest_job(ws_root: Path):
    jobs_file = ws_root / "jobs.json"
    if not jobs_file.exists():
        return None
    try:
        data = json.loads(jobs_file.read_text(encoding="utf-8"))
    except Exception:
        return None
    if not isinstance(data, list) or not data:
        return None
    return data[-1]


def _find_job(ws_root: Path, job_id: str | None):
    jobs_file = ws_root / "jobs.json"
    if not jobs_file.exists():
        return None
    try:
        data = json.loads(jobs_file.read_text(encoding="utf-8"))
    except Exception:
        return None
    if not isinstance(data, list):
        return None
    if not job_id:
        return data[-1] if data else None
    for j in reversed(data):
        if j.get("id") == job_id:
            return j
    return None


def _job_log_path(ws_root: Path, job_id: str):
    return ws_root / "logs" / f"{job_id}.log"


def _print_header(job):
    t = job.get("template", "?")
    m = job.get("machine", "?")
    jid = job.get("id", "?")
    print(f"==> Watching job {jid}  template={t}  machine={m}")


def main(argv=None):
    ap = argparse.ArgumentParser(prog="osw jobs watch")
    ap.add_argument("--ws", default=".", help="Workspace root (default: .)")
    ap.add_argument("--id", help="Specific job id to watch")
    ap.add_argument(
        "--interval", type=float, default=0.25, help="Poll interval seconds"
    )
    g = ap.add_mutually_exclusive_group()
    g.add_argument(
        "--follow", dest="follow", action="store_true", help="Follow until terminal"
    )
    g.add_argument(
        "--no-follow", dest="follow", action="store_false", help="Do not follow"
    )
    ap.set_defaults(follow=True)
    args = ap.parse_args(argv)

    ws_root = Path(args.ws).resolve()
    job = _find_job(ws_root, args.id) or _latest_job(ws_root)
    if not job:
        print("No jobs to watch.", file=sys.stderr)
        return 1

    _print_header(job)
    jid = job["id"]
    log_path = _job_log_path(ws_root, jid)
    offset = 0
    last_state = job.get("state", "?")

    def emit_new():
        nonlocal offset
        if not log_path.exists():
            return
        data = log_path.read_bytes()
        if offset < len(data):
            chunk = data[offset:]
            try:
                sys.stdout.write(chunk.decode("utf-8", errors="replace"))
            except Exception:
                sys.stdout.buffer.write(chunk)
            sys.stdout.flush()
            offset = len(data)

    emit_new()
    if not args.follow:
        return 0

    while True:
        emit_new()
        j = _find_job(ws_root, jid)
        if j:
            last_state = j.get("state", last_state)
        if last_state in TERMINAL_STATES:
            break
        time.sleep(args.interval)

    emit_new()
    print(f"\n==> Job {jid} reached terminal state: {last_state}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
