# Chapter 7 — Database Migrations

## What you'll learn

- Why hand-run `ALTER TABLE` statements don't scale past one developer
- Alembic: revisions, upgrade/downgrade, autogeneration
- Zero-downtime migration patterns (the "expand/contract" approach)
- Backfilling large tables without locking them for the duration

## How to run this chapter

```bash
pip install alembic   # already in requirements.txt
cd chapter7
alembic init migrations   # only if you want to regenerate scaffolding yourself;
                           # scripts/example_migration.py shows a worked revision
cat scripts/example_migration.py
```
