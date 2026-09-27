# Chapter 3: Exercises

1. Run `EXPLAIN ANALYZE` on `SELECT * FROM events WHERE event_type = 'signup';`
   before and after indexing `event_type` alone. Does the planner actually
   use the index? Why might it choose not to (hint: think about selectivity
   — what fraction of 500k rows have `event_type = 'signup'`?).
2. Create a composite index that supports both
   `WHERE user_id = ? ORDER BY created_at DESC` in one index scan (no
   separate sort step). Verify with `EXPLAIN` that the `Sort` node disappears.
3. Drop `idx_events_payload_gin` and measure query time for a JSONB
   containment query. Recreate it and measure again. Compute the speedup.
4. Explain why `idx_events_purchases` (a partial index) is smaller and
   sometimes faster than a full index on `(user_id, event_type)` for the
   specific query it targets.

## Common mistakes

- Indexing every column "just in case." Each index slows down every
  `INSERT`/`UPDATE`/`DELETE` on that table (it must maintain every index),
  and consumes disk + cache space that could hold more useful data.
- Assuming an index helps without checking `EXPLAIN`. Selectivity, not
  existence, decides whether the planner uses it.
- Comparing "cost" numbers across different queries as if they were
  milliseconds — they're only meaningful relative to other plans for the
  *same* query on the *same* system.

## Production considerations

- Creating an index on a large, live table with plain `CREATE INDEX` takes
  an exclusive lock that blocks writes for the duration. Use
  `CREATE INDEX CONCURRENTLY` in production (slower to build, but doesn't
  block writes) — covered further in Chapter 7 (migrations).
- Set up `pg_stat_statements` in any real deployment — it tells you which
  queries actually consume the most cumulative time, which is usually not
  the query you'd guess by eyeballing the code.
- Re-run `ANALYZE` (or trust autovacuum) after bulk loads — stale
  statistics are one of the most common causes of a sudenly-bad query plan
  after a data migration.
