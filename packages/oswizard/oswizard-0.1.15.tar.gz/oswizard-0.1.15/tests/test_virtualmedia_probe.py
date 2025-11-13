from __future__ import annotations
from typing import Any, Dict
from oswizard.virtualmedia_probe import probe_virtualmedia_slots, CANDIDATES


class _Resp:
    def __init__(self, ok: bool, payload: Dict[str, Any]):
        self.ok = ok
        self._payload = payload

    def json(self):
        return self._payload


class _Sess:
    def __init__(self, mapping):
        self._mapping = mapping

    def get(self, url: str, timeout: int = 10):
        for key, resp in self._mapping.items():
            if url.endswith(key):
                return resp
        # simulate 404/bad
        return _Resp(False, {})


def test_probe_finds_counts():
    mapping = {
        CANDIDATES[0]: _Resp(True, {"Members": [1, 2]}),
        CANDIDATES[1]: _Resp(True, {"members": [1]}),
        CANDIDATES[2]: _Resp(False, {}),
    }
    sess = _Sess(mapping)
    out = probe_virtualmedia_slots("https://bmc.example", sess)  # type: ignore[arg-type]
    assert (CANDIDATES[0], 2) in out
    assert (CANDIDATES[1], 1) in out
    # we do not include failing endpoint
    assert all(path != CANDIDATES[2] for path, _ in out)
