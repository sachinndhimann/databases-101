# Chapter 7: Exercises

1. Set up a real Alembic project against this repo's Postgres (`alembic
   init migrations`, point `sqlalchemy.url` at `POSTGRES_URL` from `.env`),
   then create and run a migration that adds `products.weight_kg` for real.
2. Run `batched_backfill.py` against the seeded `products` table (5 rows —
   small on purpose so you can watch each batch print). Add a `CHECK
   (weight_kg > 0)` constraint using the `NOT VALID` + `VALIDATE CONSTRAINT`
   pattern from `docs/concepts.md` afterward.
3. Write the `downgrade()` for a migration that renames a column
   (`ALTER TABLE products RENAME COLUMN name TO product_name`). Why is a
   rename actually simpler to reverse than most other schema changes?
4. Explain why deploying "rename a column" and "deploy code that expects
   the new name" as a single atomic step is risky in a rolling-deploy
   environment (multiple app instances, not all updated at the same
   instant) — and how expand/contract avoids it.

## Common mistakes

- Editing an already-applied migration file instead of writing a new one —
  this desyncs anyone who already ran the old version against their
  database; migrations are append-only history, not mutable state.
- Running `alembic --autogenerate` and applying it without reading the
  diff — autogenerate cannot tell a rename from a drop+create, and will
  happily generate a migration that destroys a column's data.
- A single giant `UPDATE` as a "backfill" on a large production table —
  locks rows for the whole duration and can bloat the write-ahead log
  enough to cause replication lag or disk pressure.

## Production considerations

- Always test `downgrade()` too, not just `upgrade()` — a migration you
  can't roll back is a migration you can't safely deploy.
- Run migrations as a distinct deploy step, before the new application
  code goes live, with monitoring in between — never bundle "run migration"
  and "restart all app servers" into one uninterruptible step.
- For genuinely large backfills (hundreds of millions of rows), consider a
  dedicated background job with checkpointing (store the last processed
  `id` so a crash resumes instead of restarting from zero) rather than a
  single long-running script.
