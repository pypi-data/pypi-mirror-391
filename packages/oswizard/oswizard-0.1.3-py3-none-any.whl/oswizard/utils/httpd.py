from __future__ import annotations
from pathlib import Path
from typing import Tuple
import threading
import socket
import contextlib
import http.server
import functools
import os


class _ThreadingHTTPServer(http.server.ThreadingHTTPServer):
    # allow quick reuse if we bounce the worker
    allow_reuse_address = True


def _pick_host_for_url(bind_host: str) -> str:
    """
    Return the host to place in the URL. If we bind on 0.0.0.0,
    try to pick a sensible outward-facing IP, else just echo back.
    """
    if bind_host and bind_host != "0.0.0.0":
        return bind_host
    # best-effort local IP detection
    with contextlib.closing(socket.socket(socket.AF_INET, socket.SOCK_DGRAM)) as s:
        try:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
        except Exception:
            return "127.0.0.1"


def serve_file_http(
    file_path: str | Path, host: str = "0.0.0.0", port: int = 0
) -> Tuple[str, _ThreadingHTTPServer, threading.Thread]:
    """
    Serve a *single existing file* from a tiny threaded HTTP server.

    Returns: (url, server, thread)

    - If port=0, an ephemeral port is chosen.
    - The server runs in a daemon thread; keep a reference if you want to shut it down later:
        server.shutdown(); thread.join()
    """
    p = Path(file_path).resolve()
    if not p.is_file():
        raise FileNotFoundError(f"{p} does not exist or is not a file")

    # Prefer directory= handler (3.10+); otherwise fallback to chdir wrapper.
    handler: type[http.server.SimpleHTTPRequestHandler]
    try:
        handler = functools.partial(
            http.server.SimpleHTTPRequestHandler, directory=str(p.parent)
        )  # type: ignore[arg-type]
    except TypeError:
        # Old Python fallback: change cwd only for the handler lifetime.
        class _CWDHandler(http.server.SimpleHTTPRequestHandler):
            def translate_path(self, path):
                # map to our file's parent
                old = os.getcwd()
                try:
                    os.chdir(str(p.parent))
                    return super().translate_path(path)
                finally:
                    os.chdir(old)

        handler = _CWDHandler  # type: ignore[assignment]

    httpd = _ThreadingHTTPServer((host, port), handler)
    actual_port = httpd.server_port
    url_host = _pick_host_for_url(host)

    thr = threading.Thread(
        target=httpd.serve_forever, name="osw-mini-httpd", daemon=True
    )
    thr.start()

    url = f"http://{url_host}:{actual_port}/{p.name}"
    return url, httpd, thr
