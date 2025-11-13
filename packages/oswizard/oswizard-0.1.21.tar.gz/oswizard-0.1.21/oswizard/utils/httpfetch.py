# oswizard/utils/httpfetch.py
import http.server
import socketserver
import threading
import urllib.request
import os
from pathlib import Path


def stage_iso_to_http(src_url: str, dest_path: Path, port: int = 8082) -> str:
    """Download an ISO and start an HTTP server to serve it."""
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    print(f"[info] Downloading {src_url} → {dest_path}")
    urllib.request.urlretrieve(src_url, dest_path)
    print(f"[info] ISO downloaded ({dest_path.stat().st_size / 1024 / 1024:.1f} MB)")

    # Serve directory via HTTP
    class Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=str(dest_path.parent), **kwargs)

    def serve():
        with socketserver.TCPServer(("", port), Handler) as httpd:
            print(f"[info] Serving {dest_path.parent} on port {port}")
            httpd.serve_forever()

    thread = threading.Thread(target=serve, daemon=True)
    thread.start()

    host = os.environ.get("HOST", "localhost")
    return f"http://{host}:{port}/{dest_path.name}"


def guess_best_host():
    import socket

    try:
        return socket.gethostbyname(socket.gethostname())
    except Exception:
        return "localhost"
