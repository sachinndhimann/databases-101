# Chapter 5 — SQLAlchemy ORM

## What you'll learn

- SQLAlchemy Core vs the ORM — when to use which
- Declarative models, relationships (`relationship()`, back-populates)
- Sessions, the unit-of-work pattern, and when flush/commit actually happen
- The N+1 query problem, and how `joinedload`/`selectinload` fix it

## How to run this chapter

```bash
docker exec -i db101-postgres psql -U db101 -d db101 < ../chapter1/sql/setup.sql
docker exec -i db101-postgres psql -U db101 -d db101 < ../chapter1/sql/seed.sql
python scripts/models.py         # defines the ORM models (import target)
python scripts/n_plus_one_demo.py
```
