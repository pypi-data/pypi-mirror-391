from __future__ import annotations

import subprocess


def _run(cmd: list[str]) -> str:
    out = subprocess.check_output(cmd, text=True).strip()
    return out


def test_cli_version_flag_and_cmd_match():
    # Both should print the same semantic version (e.g., "0.1.0")
    v_flag = _run(["osw", "--version"])
    v_cmd = _run(["osw", "version"])
    assert v_flag == v_cmd
    # quick sanity: it should look like a version string
    assert any(ch.isdigit() for ch in v_flag)
