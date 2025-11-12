from __future__ import annotations
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential_jitter,
    retry_if_exception_type,
)


# Generic network/backoff retry: 5 attempts, 0.5s..10s with jitter
def net_retry(exc_types: tuple[type[BaseException], ...] = (Exception,)):
    return retry(
        reraise=True,
        stop=stop_after_attempt(5),
        wait=wait_exponential_jitter(initial=0.5, max=10.0),
        retry=retry_if_exception_type(exc_types),
    )
