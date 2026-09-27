# Chapter 3: Concepts

## Reading EXPLAIN

```sql
EXPLAIN ANALYZE SELECT * FROM events WHERE user_id = 42;
```

```
Index Scan using idx_events_user_id on events  (cost=0.42..8.44 rows=1 width=64)
                                                (actual time=0.021..0.023 rows=3 loops=1)
  Index Cond: (user_id = 42)
Planning Time: 0.112 ms
Execution Time: 0.041 ms
```

- **`cost=0.42..8.44`**: planner's *estimate*, in arbitrary units (startup
  cost .. total cost) — not milliseconds. Only comparable to other plans on
  the same system.
- **`rows=1`**: planner's estimated row count vs. **`actual ... rows=3`**:
  what actually came back. A big gap between estimated and actual rows means
  stale statistics (`ANALYZE` the table) or a query the planner can't
  estimate well (e.g. a function on a column).
- **`Index Scan`** vs **`Seq Scan`**: whether an index was used at all.
  A `Seq Scan` on a huge table you expected to be indexed is your first clue
  something's wrong — either the index doesn't exist, isn't selective
  enough for the planner to prefer it, or the query can't use it (see below).
- Always use `EXPLAIN (ANALYZE, BUFFERS)` when tuning for real — `BUFFERS`
  shows actual disk/cache hits, which is often the real bottleneck, not CPU.

## Index types

| Index type | Good for | Example |
|---|---|---|
| B-tree (default) | equality, range, sorting | `WHERE price > 100`, `ORDER BY created_at` |
| Hash | equality only, no range | rarely worth it over B-tree in Postgres |
| GIN | full-text search, JSONB containment, arrays | `WHERE tags @> ARRAY['sale']` |
| GiST | geometric data, ranges, nearest-neighbor | `WHERE location <-> point '(1,2)'` |
| Partial | index only a subset of rows | `CREATE INDEX ... WHERE status = 'pending'` |
| Composite (multi-column) | queries filtering/sorting on multiple columns together | `(user_id, created_at)` |

## Why the planner might ignore your index

1. **Low selectivity**: if a `WHERE status = 'active'` matches 90% of rows,
   a sequential scan is genuinely cheaper than jumping through an index for
   almost every row. This is not a bug — it's correct.
2. **Function on the indexed column**: `WHERE lower(email) = 'x'` can't use
   a plain index on `email`. Fix with a functional/expression index:
   `CREATE INDEX ON users (lower(email));`
3. **Type mismatch**: comparing a `text` column to an `integer` literal can
   force a cast that defeats the index.
4. **Stale statistics**: run `ANALYZE table_name;` after large data changes.
5. **Small table**: the planner correctly decides a seq scan of 200 rows
   beats the overhead of an index lookup.

## Composite index column order matters

An index on `(user_id, created_at)` supports:
- `WHERE user_id = ?` alone
- `WHERE user_id = ? AND created_at > ?`
- `WHERE user_id = ? ORDER BY created_at`

It does **not** efficiently support `WHERE created_at > ?` alone — the
leftmost column must be constrained for the index to be used at all
(same rule in both Postgres and MySQL).

## PostgreSQL vs MySQL query planning

| Aspect | PostgreSQL | MySQL (InnoDB) |
|---|---|---|
| Plan inspection | `EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON)` | `EXPLAIN ANALYZE` (8.0.18+) or `EXPLAIN FORMAT=JSON` |
| Statistics | `ANALYZE`, auto-vacuum daemon runs it periodically | `ANALYZE TABLE`, auto-recalculated on ~10% change |
| Index hints | Generally discouraged; fix via query/index design | Supports explicit `USE INDEX` / `FORCE INDEX` hints |
| Covering indexes | `INCLUDE` clause since PG11 | Automatic via secondary index + primary key (clustered) |
| Clustered storage | Heap table, indexes point to heap (TID) | Table itself IS the primary key's B-tree (InnoDB) — secondary index lookups do 2 hops |
