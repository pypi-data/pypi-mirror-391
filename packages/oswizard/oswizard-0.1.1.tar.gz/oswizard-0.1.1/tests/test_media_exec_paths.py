# tests/test_media_exec_paths.py
import os
from oswizard import media


def test_mount_iso_exec_basic(monkeypatch):
    calls = []

    def fake_curl(args):
        calls.append(args)
        return 0, "OK", ""

    monkeypatch.setattr(media, "_curl", fake_curl)

    res = media.mount_iso(
        bmc="idrac-10.0.0.5",
        iso_url="https://x/iso.iso",
        username="root",
        password="p",
        vendor="dell-idrac",
        use_session=False,
        dry_run=False,
    )
    assert res.ok, res.message
    assert any("EjectMedia" in " ".join(a) for a in calls)
    assert any("InsertMedia" in " ".join(a) for a in calls)


def test_mount_iso_exec_session(monkeypatch):
    calls = []

    def fake_curl(args):
        calls.append(args)
        if "/SessionService/Sessions" in args:
            hdr = (
                "HTTP/1.1 201 Created\r\n"
                "X-Auth-Token: T123\r\n"
                "Location: https://bmc/redfish/v1/SessionService/Sessions/42\r\n\r\n"
            )
            return 0, hdr, ""
        return 0, "OK", ""

    monkeypatch.setattr(media, "_curl", fake_curl)

    os.environ.pop("BMC_USER", None)
    os.environ.pop("BMC_PASS", None)

    res = media.mount_iso(
        bmc="idrac-10.0.0.5",
        iso_url="https://x/iso.iso",
        username="root",
        password="p",
        vendor="dell-idrac",
        use_session=True,
        dry_run=False,
    )
    assert res.ok, res.message
    joined = " | ".join(" ".join(a) for a in calls)
    assert "/SessionService/Sessions" in joined
    assert "EjectMedia" in joined
    assert "InsertMedia" in joined
