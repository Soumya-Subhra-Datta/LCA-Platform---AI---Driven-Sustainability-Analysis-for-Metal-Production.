import time

_payload = None
_built_at = 0.0
TTL_SECONDS = 10


def get_cached(factory):
    global _payload, _built_at
    now = time.time()
    if _payload is not None and (now - _built_at) < TTL_SECONDS:
        return _payload
    _payload = factory()
    _built_at = now
    return _payload


def invalidate():
    global _payload
    _payload = None
