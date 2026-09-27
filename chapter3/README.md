# Chapter 3 — Indexing & Query Optimization

## What you'll learn

- How `EXPLAIN` / `EXPLAIN ANALYZE` works and how to read the plan tree
- B-tree, hash, GIN, GiST, and partial/composite indexes
- How the query planner chooses (or refuses) to use an index
- Diagnosing and fixing a slow query end-to-end

## How to run this chapter

```bash
docker exec -i db101-postgres psql -U db101 -d db101 < sql/setup.sql   # generates a large table
docker exec -i db101-postgres psql -U db101 -d db101 < sql/examples.sql
python scripts/demo.py
```
