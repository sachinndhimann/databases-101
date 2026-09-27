# Chapter 2: Exercises

1. Write a query using `RANK()` to find each user's single largest order.
2. Rewrite the `NOT IN` query in `examples.sql` (#3) to demonstrate the bug:
   insert an order with `user_id` allowed to be `NULL` (you'll need to
   temporarily drop the `NOT NULL` constraint) and show the `NOT IN` version
   returns zero rows for everyone, while `NOT EXISTS` still works correctly.
3. Using `LAG()`, compute the number of days between each user's
   consecutive orders.
4. Write a recursive CTE that generates all dates in the current month
   (a classic "date spine" used in reporting).

## Common mistakes

- Using `NOT IN` with a subquery that can return `NULL` — silently wrong,
  not an error, which makes it dangerous.
- Forgetting that window functions run *after* `WHERE` and `GROUP BY` but
  *before* the final `ORDER BY` and `LIMIT` — you cannot filter directly on
  a window function's result in the same `SELECT`'s `WHERE` clause; wrap it
  in a CTE or subquery and filter there.
- Treating a CTE as always materialized (a "temp table"). In modern
  Postgres, non-recursive CTEs can be inlined and reordered by the planner
  just like a subquery — don't rely on CTE evaluation order for side effects
  beyond `INSERT/UPDATE/DELETE ... RETURNING` CTEs, which *are* guaranteed
  to run.

## Production considerations

- Window functions over very large partitions can be memory-intensive —
  Postgres may spill to disk (`work_mem` exceeded). Watch for this in
  `EXPLAIN (ANALYZE, BUFFERS)` output (Chapter 3).
- Recursive CTEs have no automatic depth limit — a bad join condition in
  the recursive term can loop until it exhausts memory or disk. Always add
  a sane `WHERE depth < N` guard when the recursion depth isn't naturally
  bounded by the data.
