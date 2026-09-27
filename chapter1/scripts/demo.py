"""
Chapter 1 demo: connect to Postgres, run queries, and print results.
Run: python scripts/demo.py   (from inside chapter1/, with .venv active)
"""
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


def run_query(cur, title, sql):
    print(f"\n=== {title} ===")
    cur.execute(sql)
    rows = cur.fetchall()
    if rows:
        print(tabulate(rows, headers="keys", tablefmt="psql"))
    else:
        print("(no rows)")


def main():
    conn = psycopg2.connect(**DSN)
    conn.autocommit = True
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        run_query(cur, "Users and their orders", """
            SELECT u.full_name, o.id AS order_id, o.status
            FROM users u JOIN orders o ON o.user_id = u.id
            ORDER BY u.full_name;
        """)

        run_query(cur, "Order totals", """
            SELECT o.id AS order_id, SUM(oi.quantity * oi.unit_price) AS total
            FROM orders o JOIN order_items oi ON oi.order_id = o.id
            GROUP BY o.id ORDER BY o.id;
        """)

        print("\n=== BREAK IT: violating a CHECK constraint ===")
        try:
            cur.execute(
                "INSERT INTO products (sku, name, price, stock_qty) "
                "VALUES ('SKU-BAD', 'Broken', -5, 0);"
            )
        except Exception as e:
            print(f"Got the expected error: {e.pgcode} - {str(e).strip()}")

    conn.close()


if __name__ == "__main__":
    main()
