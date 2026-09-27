# Chapter 2 — SQL Deep Dive

## What you'll learn

- All join types and what they actually do internally
- Subqueries: scalar, correlated, `EXISTS` vs `IN`
- Common Table Expressions (CTEs), including recursive CTEs
- Window functions: `ROW_NUMBER`, `RANK`, running totals, `LAG`/`LEAD`

## How to run this chapter

```bash
docker exec -i db101-postgres psql -U db101 -d db101 < ../chapter1/sql/setup.sql
docker exec -i db101-postgres psql -U db101 -d db101 < ../chapter1/sql/seed.sql
docker exec -i db101-postgres psql -U db101 -d db101 < sql/examples.sql
python scripts/demo.py
```
