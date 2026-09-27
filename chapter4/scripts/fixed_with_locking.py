"""
Chapter 4: the fix — SELECT ... FOR UPDATE serializes the two transactions
so the second one sees the first one's committed decrement.
"""
import os
import threading
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


def buy_one_safe():
    conn = psycopg2.connect(**DSN)
    with conn.cursor() as cur:
        cur.execute(
            "SELECT stock_qty FROM products WHERE id = %s FOR UPDATE;", (PRODUCT_ID,)
        )
        current = cur.fetchone()[0]
        cur.execute(
            "UPDATE products SET stock_qty = %s WHERE id = %s;",
            (current - 1, PRODUCT_ID),
        )
    conn.commit()  # releases the row lock
    conn.close()


def main():
    reset_stock()
    threads = [threading.Thread(target=buy_one_safe) for _ in range(2)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    conn = psycopg2.connect(**DSN)
    with conn.cursor() as cur:
        cur.execute("SELECT stock_qty FROM products WHERE id = %s;", (PRODUCT_ID,))
        final = cur.fetchone()[0]
    conn.close()

    print(f"Expected stock_qty = 48, actual = {final} (FOR UPDATE prevents the lost update)")


if __name__ == "__main__":
    main()
