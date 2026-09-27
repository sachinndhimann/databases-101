"""
Chapter 7: batched backfill script — the "backfill" phase of expand/contract,
run standalone so each batch commits independently and the table is never
locked for the full duration.
"""
import os
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

BATCH_SIZE = 500
SLEEP_BETWEEN_BATCHES = 0.05  # be a good citizen -- let other queries interleave


def backfill():
    conn = psycopg2.connect(**DSN)
    conn.autocommit = True  # each batch below is its own implicit transaction
    total_updated = 0
    with conn.cursor() as cur:
        while True:
            cur.execute(
                """
                UPDATE products
                SET weight_kg = 1.0
                WHERE id IN (
                    SELECT id FROM products WHERE weight_kg IS NULL LIMIT %s
                );
                """,
                (BATCH_SIZE,),
            )
            updated = cur.rowcount
            total_updated += updated
            print(f"Backfilled {updated} rows (total so far: {total_updated})")
            if updated == 0:
                break
            time.sleep(SLEEP_BETWEEN_BATCHES)
    conn.close()
    print(f"Done. {total_updated} rows backfilled.")


if __name__ == "__main__":
    backfill()
