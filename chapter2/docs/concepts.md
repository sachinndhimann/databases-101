# Chapter 2: Concepts

## Joins — what actually happens

A join combines rows from two tables based on a matching condition. The
*type* of join controls what happens to rows that have no match.

| Join | Keeps unmatched left rows? | Keeps unmatched right rows? |
|---|---|---|
| `INNER JOIN` | No | No |
| `LEFT JOIN` | Yes (nulls for right side) | No |
| `RIGHT JOIN` | No | Yes (nulls for left side) |
| `FULL OUTER JOIN` | Yes | Yes |
| `CROSS JOIN` | every row × every row (no condition) | — |

Internally, the query planner picks one of three physical strategies
regardless of which SQL join keyword you wrote:

- **Nested loop**: for each row in the outer table, scan the inner table.
  Fine for small tables or when the inner side has a usable index.
  O(n·m) without an index.
- **Hash join**: build an in-memory hash table on the smaller side, probe
  it with the larger side. Good for large, unindexed equality joins.
- **Merge join**: both sides are already sorted (or get sorted), then
  merged like a zipper. Good when both sides are pre-sorted by the join key.

You don't choose the strategy — the planner does, based on table
statistics. Chapter 3 shows you how to read `EXPLAIN` to see which one it
picked and why.

## Subqueries

- **Scalar subquery**: returns exactly one value, used anywhere a value is
  expected: `WHERE price > (SELECT AVG(price) FROM products)`.
- **Correlated subquery**: references a column from the outer query, so it
  re-runs conceptually once per outer row: `WHERE EXISTS (SELECT 1 FROM
  orders o WHERE o.user_id = u.id)`.
- **`IN` vs `EXISTS`**: `IN` materializes the subquery's result set and
  checks membership; `EXISTS` short-circuits on the first match. For large
  subquery result sets, `EXISTS` (or a `JOIN` with `DISTINCT`) is usually
  faster and handles `NULL` correctly — `NOT IN` with a `NULL` in the
  subquery's results silently returns zero rows, a classic bug.

## Common Table Expressions (CTEs)

A CTE (`WITH x AS (...)`) names a subquery so you can reference it, possibly
multiple times, and read the query top-to-bottom. It doesn't change what's
computed, mainly how readable the query is — though PostgreSQL 12+ may
inline non-recursive CTEs into the main query plan (older versions treated
every CTE as an optimization fence).

**Recursive CTEs** solve hierarchical/graph problems (org charts, category
trees, bill-of-materials) that plain SQL can't express:

```sql
WITH RECURSIVE subordinates AS (
    SELECT id, manager_id, name FROM employees WHERE id = 1
    UNION ALL
    SELECT e.id, e.manager_id, e.name
    FROM employees e
    JOIN subordinates s ON e.manager_id = s.id
)
SELECT * FROM subordinates;
```

## Window functions

A window function computes a value across a set of rows *related to the
current row* without collapsing them into one row (unlike `GROUP BY`).

```sql
SELECT
    user_id, id AS order_id, created_at,
    ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY created_at) AS order_seq,
    SUM(id) OVER (PARTITION BY user_id ORDER BY created_at) AS running_sum
FROM orders;
```

- `PARTITION BY` splits rows into groups (like `GROUP BY`, but rows stay
  separate).
- `ORDER BY` inside `OVER(...)` controls running/ranking calculations.
- `ROW_NUMBER()` — unique sequential number, ties broken arbitrarily.
- `RANK()` — same rank for ties, next rank skips (1,1,3).
- `DENSE_RANK()` — same rank for ties, next rank doesn't skip (1,1,2).
- `LAG(col, n)` / `LEAD(col, n)` — value from n rows before/after.

## PostgreSQL vs MySQL

| Feature | PostgreSQL | MySQL |
|---|---|---|
| Window functions | Supported since 8.4 | Supported since 8.0 (not in 5.7) |
| Recursive CTEs | Supported since 8.4 | Supported since 8.0 |
| `FULL OUTER JOIN` | Supported | **Not supported** — emulate with `LEFT JOIN UNION RIGHT JOIN` |
| `EXISTS` optimization | Planner rewrites well | Historically weaker; a `JOIN` rewrite is often faster on old versions |
