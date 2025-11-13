"""
netdetect.py — lightweight network helper for OSWizard

Auto-detects a reachable local IP (non-loopback) and assigns a default HTTP port.
Used during PREPARE to populate job.vars['http_host'] and ['http_port'].
"""

import socket


def detect_http_host_port(default_port: int = 8080):
    """
    Detect a reachable local IP and return (ip, port).

    This tries to determine which outbound interface can reach the Internet.
    If no valid route is found, it safely falls back to 127.0.0.1.
    """
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
    except Exception:
        ip = "127.0.0.1"
    return ip, default_port


if __name__ == "__main__":
    ip, port = detect_http_host_port()
    print(f"Auto-detected HTTP endpoint: {ip}:{port}")
