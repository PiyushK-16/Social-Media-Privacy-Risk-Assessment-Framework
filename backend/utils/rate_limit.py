"""rate_limit.py - tiny in-memory fixed-window rate limiter (per client IP).
Good enough for a student project; use Redis / a proxy limiter in production."""
import threading
import time
from collections import defaultdict, deque


class RateLimiter:
    def __init__(self, max_calls, window_seconds=60):
        self.max_calls, self.window = max_calls, window_seconds
        self._hits = defaultdict(deque)
        self._lock = threading.Lock()

    def allow(self, key):
        now = time.monotonic()
        with self._lock:
            q = self._hits[key]
            while q and now - q[0] > self.window:
                q.popleft()
            if len(q) >= self.max_calls:
                return False
            q.append(now)
            return True
