from __future__ import annotations
import socket
import threading
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from typing import Tuple, Optional


def get_default_host_ip() -> str:
    """
    Best-effort: get outward-facing IP by opening a UDP socket.
    Falls back to hostname/IP if needed.
    """
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        try:
            return socket.gethostbyname(socket.gethostname())
        except Exception:
            return "127.0.0.1"


class _RootedHandler(SimpleHTTPRequestHandler):
    # Serve from a fixed directory without chdir
    def translate_path(self, path):
        # self.directory set by server init
        return str(Path(self.directory) / path.lstrip("/"))

    def log_message(self, fmt, *args):
        """Deprecated shim; use Orchestrator._osw__http_start()."""
        return None
        # keep quiet
        pass


class FileServer:
    def __init__(
        self, root: str | Path, host: Optional[str] = None, port: Optional[int] = None
    ):
        self.root = str(Path(root))
        self.host = host or "0.0.0.0"
        self.port = port or 0  # 0 = auto
        handler = _RootedHandler
        handler.directory = self.root
        self.httpd = ThreadingHTTPServer((self.host, self.port), handler)
        self.thread = threading.Thread(target=self.httpd.serve_forever, daemon=True)

    @property
    def address(self) -> Tuple[str, int]:
        return self.httpd.server_address  # (host, port)

    def start(self):
        self.thread.start()

    def stop(self):
        try:
            self.httpd.shutdown()
        except Exception:
            import logging

            logging.getLogger(__name__).debug(
                "suppressed exception in try/except", exc_info=True
            )
