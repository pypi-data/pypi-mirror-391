from __future__ import annotations


import oswizard.orchestrator as orch


def test_osw_phase5_maybe_rescue_true(monkeypatch, tmp_path):
    calls = {}

    def fake_apply(payload, ttl_minutes=None):
        calls["payload"] = payload
        calls["ttl"] = ttl_minutes

    monkeypatch.setattr(orch, "apply_rescue_patch", fake_apply, raising=True)

    m = {
        "rescue": {
            "enabled": True,
            "payload_dir": str(tmp_path / "rescue"),
            "ttl_minutes": 15,
        }
    }
    (tmp_path / "rescue" / "scripts").mkdir(
        parents=True, exist_ok=True
    )  # shape, not executed here
    assert orch.osw_phase5_maybe_rescue(m, "job-1") is True
    assert calls["payload"] == str(tmp_path / "rescue")
    assert calls["ttl"] == 15


def test_osw_phase5_maybe_rescue_false(monkeypatch):
    # No rescue key
    assert orch.osw_phase5_maybe_rescue({}, "job-x") is False
    # Disabled
    m = {"rescue": {"enabled": False}}
    assert orch.osw_phase5_maybe_rescue(m, "job-y") is False
