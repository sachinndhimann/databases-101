"""
Chapter 6: cache stampede demo — many concurrent "requests" all miss the
cache at once, then the single-flight lock fix.
"""
import os
import threading
import time
from pathlib import Path

import redis
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[2] / ".env")
r = redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379/0"))

CACHE_KEY = "expensive:report"
LOCK_KEY = "lock:expensive:report"
db_hits = []
lock_obj = threading.Lock()


def expensive_recompute():
    with lock_obj:
        db_hits.append(1)
    time.sleep(0.5)
    return "computed-value"


def get_without_protection():
    value = r.get(CACHE_KEY)
    if value:
        return value.decode()
    value = expensive_recompute()   # every concurrent miss recomputes!
    r.setex(CACHE_KEY, 5, value)
    return value


def get_with_single_flight():
    value = r.get(CACHE_KEY)
    if value:
        return value.decode()

    got_lock = r.set(LOCK_KEY, "1", nx=True, ex=5)
    if got_lock:
        try:
            value = expensive_recompute()
            r.setex(CACHE_KEY, 5, value)
            return value
        finally:
            r.delete(LOCK_KEY)
    else:
        # another thread is already recomputing -- wait briefly and retry cache
        time.sleep(0.6)
        value = r.get(CACHE_KEY)
        return value.decode() if value else expensive_recompute()


def run_stampede(fn, label):
    global db_hits
    db_hits = []
    r.delete(CACHE_KEY, LOCK_KEY)
    threads = [threading.Thread(target=fn) for _ in range(20)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    print(f"{label}: {len(db_hits)} expensive recomputes for 20 concurrent requests")


def main():
    run_stampede(get_without_protection, "WITHOUT single-flight lock")
    run_stampede(get_with_single_flight, "WITH single-flight lock")


if __name__ == "__main__":
    main()
