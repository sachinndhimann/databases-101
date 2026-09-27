# Database Engineering 101

A hands-on, build-and-break learning repository covering PostgreSQL, MySQL,
SQL optimization, SQLAlchemy, Redis caching, and database migrations —
from intermediate concepts to production-oriented database engineering.

## Philosophy

Every topic follows this loop:

```
CONCEPT → MENTAL MODEL → DIAGRAM → SQL/CODE → RUN IT → OBSERVE → EXPLAIN WHY → OPTIMIZE → BREAK IT → FIX IT
```

You are not meant to just read this. Run every script. Break things on purpose.
Read the "Common mistakes" and "Production considerations" sections — that's
where the real engineering judgment lives.

## Curriculum

| Chapter | Topic | Focus |
|---|---|---|
| 1 | Database Fundamentals | Tables, keys, constraints, normalization, ER modeling |
| 2 | SQL Deep Dive | Joins, subqueries, CTEs, window functions |
| 3 | Indexing & Query Optimization | EXPLAIN/ANALYZE, index types, query planning |
| 4 | Transactions & Concurrency | ACID, isolation levels, locking, deadlocks |
| 5 | SQLAlchemy ORM | Core vs ORM, sessions, relationships, N+1 problem |
| 6 | Redis Caching | Cache-aside, TTLs, invalidation, cache stampedes |
| 7 | Database Migrations | Alembic, versioning, zero-downtime migrations |
| 8 | PostgreSQL vs MySQL & Production | Engine differences, scaling, backups, monitoring |

Each chapter directory contains:

```
chapterN/
├── README.md          # what you'll learn, how to run it
├── docs/               # concepts, mental models, diagrams
├── sql/                # setup.sql, examples.sql, exercises.sql (where applicable)
├── scripts/            # runnable Python demos
└── exercises/          # exercises.md with problems + solutions
```

## Prerequisites

- Docker + Docker Compose
- Python 3.10+
- `make` (optional but recommended — all commands also work run directly)

## Setup

```bash
cp .env.example .env
make up            # starts Postgres, MySQL, Redis, and Adminer (localhost:8080)
make venv && source .venv/bin/activate
make install
```

Verify everything is up:

```bash
docker compose ps
```

## Working through the curriculum

Go chapter by chapter, in order — later chapters assume the schema and
concepts from Chapter 1. Inside each chapter:

```bash
cd chapter1
cat README.md                                    # read first
make -C .. seed-ch1                               # or run the .sql files manually
python scripts/demo.py                            # run the hands-on demo
```

For chapters without a Makefile target, load SQL directly:

```bash
docker exec -i db101-postgres psql -U db101 -d db101 < chapterN/sql/setup.sql
```

## Databases: Postgres AND MySQL

This repo does not pretend Postgres and MySQL are the same engine. Primary
hands-on examples use PostgreSQL; MySQL equivalents and behavioral
differences are called out explicitly, especially in:

- `chapter1/docs/concepts.md` (constraint/type differences)
- `chapter3/docs/` (query planner differences)
- `chapter4/docs/` (isolation level defaults)
- `chapter8/docs/postgres-vs-mysql.md` (the full comparison matrix)

## Repository map

```
database-101/
├── README.md
├── docker-compose.yml
├── .env.example
├── requirements.txt
├── Makefile
├── chapter1/  Database Fundamentals
├── chapter2/  SQL Deep Dive
├── chapter3/  Indexing & Query Optimization
├── chapter4/  Transactions & Concurrency
├── chapter5/  SQLAlchemy ORM
├── chapter6/  Redis Caching
├── chapter7/  Database Migrations
├── chapter8/  Postgres vs MySQL & Production
└── workflows/ Backup, monitoring, scaling playbooks
```
