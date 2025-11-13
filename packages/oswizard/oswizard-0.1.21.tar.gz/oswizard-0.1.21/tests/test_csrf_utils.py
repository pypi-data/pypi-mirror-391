from __future__ import annotations
from requests import Session
from oswizard.utils import csrf


def test_harvest_csrf_from_cookies_found():
    s = Session()
    s.cookies.set("csrftoken", "abc123")
    assert csrf.harvest_csrf_from_cookies(s) == "abc123"


def test_harvest_csrf_from_cookies_fallback_header():
    s = Session()
    s.cookies.set("Something", "x")
    s.cookies.set("X-XSRF-TOKEN", "zzZ")
    # harvest should be case-insensitive and find fallback too
    assert csrf.harvest_csrf_from_cookies(s) in ("zzZ", "x")


def test_attach_csrf_headers_sets_common_keys():
    s = Session()
    s.cookies.set("xsrf-token", "tok")
    csrf.attach_csrf_headers(s)
    assert s.headers.get("X-CSRF-Token") == "tok"
    assert s.headers.get("X-XSRF-TOKEN") == "tok"
