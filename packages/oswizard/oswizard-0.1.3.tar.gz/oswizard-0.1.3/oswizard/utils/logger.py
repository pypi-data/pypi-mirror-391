from __future__ import annotations

import os
import sys
import time

_LEVEL_ORDER = {"DEBUG": 10, "INFO": 20, "WARN": 30, "ERROR": 40}


def _env_level() -> int:
    try:
        lvl = os.environ.get("OSW_LOG_LEVEL", "INFO").upper()
        return _LEVEL_ORDER.get(lvl, 20)
    except Exception:
        return 20


_current_level = _env_level()


def set_level(level: str) -> None:
    """Programmatically set log level (DEBUG/INFO/WARN/ERROR)."""
    global _current_level
    try:
        _current_level = _LEVEL_ORDER.get(str(level).upper(), 20)
    except Exception:
        _current_level = 20


def log(message: str, level: str = "INFO") -> None:
    """
    Log a message. Accepts level case-insensitively.
    Compatible with existing calls like: log("msg", "info")
    Never raises.
    """
    try:
        lvl = str(level).upper()
        if lvl not in _LEVEL_ORDER:
            lvl = "INFO"
        if _LEVEL_ORDER[lvl] < _current_level:
            return
        ts = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        sys.stderr.write(f"[{ts}] [{lvl}] {message}\n")
    except Exception as e:
        # Last-ditch: write something and swallow
        try:
            sys.stderr.write(f"[WARN] logger fallback: {e!r}; msg={message!r}\n")
        except Exception as e:
            try:
                sys.stderr.write(f"[WARN] logger fallback suppressed: {e!r}\n")
            except Exception:
                # nothing else we can do
                ...


def debug(msg: str) -> None:
    log(msg, "DEBUG")


def info(msg: str) -> None:
    log(msg, "INFO")


def warn(msg: str) -> None:
    log(msg, "WARN")


def error(msg: str) -> None:
    log(msg, "ERROR")
