# Chapter 4 — Transactions & Concurrency

## What you'll learn

- ACID properties, in concrete terms
- Isolation levels and the anomalies each one prevents
- Row locks, `SELECT ... FOR UPDATE`, and deadlocks
- How to reproduce a race condition, then fix it

## How to run this chapter

```bash
docker exec -i db101-postgres psql -U db101 -d db101 < ../chapter1/sql/setup.sql
docker exec -i db101-postgres psql -U db101 -d db101 < ../chapter1/sql/seed.sql
python scripts/race_condition_demo.py       # reproduces a lost-update bug
python scripts/fixed_with_locking.py        # fixes it with SELECT FOR UPDATE
```
