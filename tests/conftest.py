# tests/conftest.py
import pytest
from utils.rate_limit import limiter


def _flush_storage():
    """
    try to flush the storage of the rate limiter.
    """
    store = getattr(limiter, "storage", None) or getattr(limiter, "_storage", None)
    if store is None:
        return


    for m in ("reset", "flush", "clear_all"):
        if hasattr(store, m):
            getattr(store, m)()
            return


    for attr in ("_storage", "storage"):
        d = getattr(store, attr, None)
        if isinstance(d, dict):
            d.clear()
            return

@pytest.fixture(autouse=True)
def rate_limit_handling(request, monkeypatch):
    """
    Fixture to handle rate limiting for tests.
    If the test has the marker "no_rate_limit", it will disable rate limiting.
    Otherwise, it will enable rate limiting.
    This fixture is applied automatically to all tests.
    """
    want_disabled = request.node.get_closest_marker("no_rate_limit") is not None


    if hasattr(limiter, "enabled"):

        original_enabled = limiter.enabled
        limiter.enabled = not want_disabled
    else:
        if want_disabled:
            for attr in ("_check_request_limit", "_evaluate_limits",
                         "check_request_limit", "_check_request"):
                if hasattr(limiter, attr):
                    monkeypatch.setattr(limiter, attr,
                                        lambda *a, **kw: None, raising=True)
                    break

    _flush_storage()

    yield
    _flush_storage()
    if hasattr(limiter, "enabled"):
        limiter.enabled = original_enabled
