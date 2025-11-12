import re
from pathlib import Path


def test_version_file_present_and_semver():
    vf = Path("VERSION")
    assert vf.exists(), "VERSION file should exist"
    ver = vf.read_text(encoding="utf-8").strip()
    assert re.fullmatch(r"v?\d+\.\d+\.\d+", ver), f"Bad version string: {ver!r}"


def test_oswizard_imports():
    import oswizard  # noqa: F401

    # Importing CLI module should not crash
    import oswizard.cli  # noqa: F401
