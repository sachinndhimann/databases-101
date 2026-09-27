"""
Chapter 3 demo: run a query before/after an index exists and compare
actual execution time reported by EXPLAIN ANALYZE.
"""
import os
from pathlib import Path

import psycopg2
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[2] / ".env")

DSN = {
    "host": "localhost",
    "port": os.getenv("POSTGRES_PORT", "5432"),
    "dbname": os.getenv("POSTGRES_DB", "db101"),
    "user": os.getenv("POSTGRES_USER", "db101"),
    "password": os.getenv("POSTGRES_PASSWORD", "db101pass"),
}

QUERY = "SELECT * FROM events WHERE user_id = 42;"


def explain(cur, label):
    cur.execute(f"EXPLAIN ANALYZE {QUERY}")
    plan = "\n".join(row[0] for row in cur.fetchall())
    print(f"\n=== {label} ===\n{plan}")


def main():
    conn = psycopg2.connect(**DSN)
    conn.autocommit = True
    with conn.cursor() as cur:
        cur.execute("DROP INDEX IF EXISTS idx_events_user_id;")
        explain(cur, "WITHOUT index (expect Seq Scan)")

        cur.execute("CREATE INDEX idx_events_user_id ON events(user_id);")
        cur.execute("ANALYZE events;")
        explain(cur, "WITH index (expect Index Scan)")
    conn.close()


if __name__ == "__main__":
    main()
