# Chapter 1 — Database Fundamentals

## What you'll learn

- What a relational database actually is (and isn't)
- Tables, rows, columns, keys (primary, candidate, foreign)
- Constraints: NOT NULL, UNIQUE, CHECK, DEFAULT, FOREIGN KEY
- Relationships: one-to-many, many-to-many
- Normalization (1NF → 3NF) and when to break the rules

## How to run this chapter

```bash
docker exec -i db101-postgres psql -U db101 -d db101 < sql/setup.sql
docker exec -i db101-postgres psql -U db101 -d db101 < sql/seed.sql
docker exec -i db101-postgres psql -U db101 -d db101 < sql/examples.sql
python scripts/demo.py
```

Read in this order:
1. `docs/concepts.md`
2. `docs/mental-model.md`
3. `docs/diagrams.md`
4. `sql/setup.sql` then `sql/seed.sql`
5. `sql/examples.sql`
6. `exercises/exercises.md`
