# backend/ingestion/adapters/rate_limiter.py

import threading
import time


class RateLimiter:
    """
    Thread-safe minimum-interval limiter, shared across all worker
    threads so concurrent scraping still spaces out real requests
    to the target site.
    """

    def __init__(self, min_interval_seconds: float) -> None:

        self._min_interval = min_interval_seconds
        self._lock = threading.Lock()
        self._last_request_at = 0.0

    def wait(self) -> None:

        with self._lock:

            now = time.monotonic()
            remaining = self._min_interval - (now - self._last_request_at)

            if remaining > 0:
                time.sleep(remaining)

            self._last_request_at = time.monotonic()
