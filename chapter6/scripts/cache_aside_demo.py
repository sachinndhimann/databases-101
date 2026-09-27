"""
Chapter 6: cache-aside pattern against Postgres + Redis.
Run chapter1's setup.sql + seed.sql first.
"""
import json
import os
import time
from pathlib import Path

import psycopg2
import psycopg2.extras
import redis
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[2] / ".env")

PG_DSN = dict(
    host="localhost",
    port=os.getenv("POSTGRES_PORT", "5432"),
    dbname=os.getenv("POSTGRES_DB", "db101"),
    user=os.getenv("POSTGRES_USER", "db101"),
    password=os.getenv("POSTGRES_PASSWORD", "db101pass"),
)
r = redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379/0"))

CACHE_TTL_SECONDS = 30


def fetch_product_from_db(product_id):
    """Simulates an expensive query with an artificial delay."""
    conn = psycopg2.connect(**PG_DSN)
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        time.sleep(0.3)  # pretend this is an expensive join/aggregation
        cur.execute("SELECT * FROM products WHERE id = %s;", (product_id,))
        row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


def get_product_cached(product_id):
    cache_key = f"product:{product_id}"

    cached = r.get(cache_key)
    if cached:
        print(f"[CACHE HIT]  {cache_key}")
        return json.loads(cached)

    print(f"[CACHE MISS] {cache_key} -> querying database")
    product = fetch_product_from_db(product_id)
    if product:
        r.setex(cache_key, CACHE_TTL_SECONDS, json.dumps(product, default=str))
    return product


def invalidate_product_cache(product_id):
    r.delete(f"product:{product_id}")
    print(f"[INVALIDATED] product:{product_id}")


def main():
    print("First read (expect MISS + ~0.3s delay):")
    t0 = time.time()
    get_product_cached(1)
    print(f"  took {time.time() - t0:.3f}s")

    print("\nSecond read (expect HIT + fast):")
    t0 = time.time()
    get_product_cached(1)
    print(f"  took {time.time() - t0:.3f}s")

    print("\nSimulating a write to the product, then invalidating cache:")
    invalidate_product_cache(1)

    print("\nThird read after invalidation (expect MISS again):")
    t0 = time.time()
    get_product_cached(1)
    print(f"  took {time.time() - t0:.3f}s")


if __name__ == "__main__":
    main()
