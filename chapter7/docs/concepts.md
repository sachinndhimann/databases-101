# Chapter 7: Concepts

## Why not just run ALTER TABLE by hand?

It works solo. It breaks down the moment you have:
- more than one environment (dev/staging/prod) that must end up identical
- more than one developer whose schema changes must apply in the right order
- a need to roll back a bad change safely

A migration tool (Alembic for SQLAlchemy, Flyway/Liquibase elsewhere) gives
you: an ordered, version-controlled history of schema changes; a way to
apply them idempotently to any environment; and a downgrade path.

## Alembic basics

```bash
alembic init migrations          # scaffold migrations/ directory + alembic.ini
alembic revision -m "add phone_numbers table"      # creates a new revision file
alembic revision --autogenerate -m "add index"     # diffs models vs DB, writes the migration
alembic upgrade head              # apply all pending migrations
alembic downgrade -1              # undo the last one
```

Every revision file has an `upgrade()` and a `downgrade()` function.
Alembic autogeneration is a *starting point*, not a guarantee — always read
the generated migration. It cannot detect table/column renames (it will
generate a drop + create instead of a rename) and doesn't know your data
semantics.

```python
def upgrade():
    op.add_column("products", sa.Column("weight_kg", sa.Numeric(6, 2), nullable=True))

def downgrade():
    op.drop_column("products", "weight_kg")
```

## Zero-downtime migrations: expand/contract

Never do a breaking schema change in one deploy. Split it into phases so
the old and new application code can both run against the schema
mid-rollout:

1. **Expand**: add the new column/table alongside the old one. Deploy code
   that writes to *both* old and new.
2. **Backfill**: populate the new column for existing rows, in batches
   (see below), without locking the table.
3. **Migrate reads**: deploy code that reads from the new column, still
   writing both.
4. **Contract**: once all instances are on the new code and backfill is
   verified complete, stop writing the old column, then drop it in a later
   migration.

Doing this in one step (e.g. `ALTER TABLE ... RENAME COLUMN` deployed at
the same time as code that expects the new name) causes a window where
old application instances error against the new schema, or vice versa.

## Backfilling large tables without long locks

```sql
-- BAD: single huge UPDATE holds locks and a long transaction, bloats WAL
UPDATE big_table SET new_col = compute(old_col);

-- BETTER: batch it
DO $$
DECLARE
    batch_size INT := 5000;
    rows_updated INT;
BEGIN
    LOOP
        UPDATE big_table SET new_col = compute(old_col)
        WHERE id IN (
            SELECT id FROM big_table WHERE new_col IS NULL LIMIT batch_size
        );
        GET DIAGNOSTICS rows_updated = ROW_COUNT;
        EXIT WHEN rows_updated = 0;
        COMMIT;  -- inside a DO block this requires a procedure, see note below
    END LOOP;
END $$;
```

In practice, batched backfills are usually driven from application code
(a script that loops, commits each batch, and sleeps briefly) rather than
a single PL/pgSQL block, precisely so each batch is its own short
transaction.

## Adding constraints without locking

```sql
-- Adding a CHECK/FK to a large existing table:
ALTER TABLE orders ADD CONSTRAINT positive_total CHECK (total >= 0) NOT VALID;
-- NOT VALID: instantly adds the constraint for NEW rows, doesn't scan existing rows,
-- so it takes only a brief lock.

ALTER TABLE orders VALIDATE CONSTRAINT positive_total;
-- Scans existing rows to confirm they satisfy it, but takes a much weaker
-- lock than the ADD CONSTRAINT would without NOT VALID, so writes aren't blocked.
```

Similarly, use `CREATE INDEX CONCURRENTLY` (Postgres) instead of plain
`CREATE INDEX` on any table receiving live writes.

## PostgreSQL vs MySQL migrations

| Aspect | PostgreSQL | MySQL |
|---|---|---|
| Concurrent index build | `CREATE INDEX CONCURRENTLY` | `ALGORITHM=INPLACE` (InnoDB, most DDL since 5.6) |
| Adding a column with a default | Instant metadata-only change (PG 11+, no rewrite) | Instant for `ADD COLUMN` since 8.0 (`INSTANT` algorithm), earlier versions rewrite the table |
| NOT VALID constraints | Supported | No direct equivalent — must validate via application code or triggers |
| Transactional DDL | Yes — DDL can be rolled back with the rest of a transaction | No — most DDL implicitly commits |
