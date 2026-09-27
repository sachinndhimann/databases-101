"""
Chapter 4: reproduce a lost-update race condition on purpose.

Two "concurrent" transactions both read stock_qty=50, both decrement by 1
without locking, and — because they interleave — only one decrement wins.
Run this after chapter1's setup.sql + seed.sql.
"""
import os
import threading
import time
from pathlib import Path

import psycopg2
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[2] / ".env")

DSN = dict(
    host="localhost",
    port=os.getenv("POSTGRES_PORT", "5432"),
    dbname=os.getenv("POSTGRES_DB", "db101"),
    user=os.getenv("POSTGRES_USER", "db101"),
    password=os.getenv("POSTGRES_PASSWORD", "db101pass"),
)

PRODUCT_ID = 1


def reset_stock():
    conn = psycopg2.connect(**DSN)
    conn.autocommit = True
    with conn.cursor() as cur:
        cur.execute("UPDATE products SET stock_qty = 50 WHERE id = %s;", (PRODUCT_ID,))
    conn.close()


def buy_one_unsafe(delay):
    """Read-then-write with no locking -> classic lost update."""
    conn = psycopg2.connect(**DSN)
    with conn.cursor() as cur:
        cur.execute("SELECT stock_qty FROM products WHERE id = %s;", (PRODUCT_ID,))
        current = cur.fetchone()[0]
        time.sleep(delay)  # widen the race window on purpose
        cur.execute(
            "UPDATE products SET stock_qty = %s WHERE id = %s;",
            (current - 1, PRODUCT_ID),
        )
    conn.commit()
    conn.close()


def main():
    reset_stock()
    t1 = threading.Thread(target=buy_one_unsafe, args=(0.5,))
    t2 = threading.Thread(target=buy_one_unsafe, args=(0.5,))
    t1.start()
    t2.start()
    t1.join()
    t2.join()

    conn = psycopg2.connect(**DSN)
    with conn.cursor() as cur:
        cur.execute("SELECT stock_qty FROM products WHERE id = %s;", (PRODUCT_ID,))
        final = cur.fetchone()[0]
    conn.close()

    print(f"Expected stock_qty = 48 (two decrements from 50)")
    print(f"Actual stock_qty   = {final}")
    if final != 48:
        print("Lost update reproduced: one of the two decrements was overwritten.")


if __name__ == "__main__":
    main()
