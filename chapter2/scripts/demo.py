"""Chapter 2 demo: run window-function and CTE queries, print results."""
import os
from pathlib import Path

import psycopg2
import psycopg2.extras
from dotenv import load_dotenv
from tabulate import tabulate

load_dotenv(Path(__file__).resolve().parents[2] / ".env")

DSN = {
    "host": "localhost",
    "port": os.getenv("POSTGRES_PORT", "5432"),
    "dbname": os.getenv("POSTGRES_DB", "db101"),
    "user": os.getenv("POSTGRES_USER", "db101"),
    "password": os.getenv("POSTGRES_PASSWORD", "db101pass"),
}

WINDOW_QUERY = """
WITH order_totals AS (
    SELECT o.id AS order_id, o.user_id, o.created_at,
           SUM(oi.quantity * oi.unit_price) AS total
    FROM orders o JOIN order_items oi ON oi.order_id = o.id
    GROUP BY o.id, o.user_id, o.created_at
)
SELECT
    user_id, order_id, total,
    ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY created_at) AS order_seq,
    SUM(total) OVER (PARTITION BY user_id ORDER BY created_at) AS running_total
FROM order_totals
ORDER BY user_id, created_at;
"""


def main():
    conn = psycopg2.connect(**DSN)
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute(WINDOW_QUERY)
        rows = cur.fetchall()
        print(tabulate(rows, headers="keys", tablefmt="psql"))
    conn.close()


if __name__ == "__main__":
    main()
