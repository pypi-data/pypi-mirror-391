import time
from pathlib import Path
from .config import Workspace
from .orchestrator import Orchestrator


def run_worker(ws_path: str = "./osw-work", interval: int = 2, dry_run: bool = True):
    ws = Workspace.init(Path(ws_path))
    try:
        while True:
            Orchestrator(ws, dry_run=dry_run).run_once()
            time.sleep(interval)
    except KeyboardInterrupt:
        import logging

        logging.getLogger(__name__).debug(
            "suppressed exception in try/except", exc_info=True
        )
