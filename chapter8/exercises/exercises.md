# Chapter 8: Exercises

1. Take one query from Chapter 2 or Chapter 3 and write out how you'd
   expect its `EXPLAIN` output to differ conceptually if it ran on MySQL
   instead of Postgres (you don't need a MySQL instance — reason from
   `docs/postgres-vs-mysql.md`).
2. Design a backup strategy for this repo's Postgres container: what would
   you run, on what schedule, and how would you test the restore? Write it
   as a runbook (see `workflows/backup.md` for a starting template).
3. Given the "pragmatic order of operations" in `docs/production.md`,
   diagnose a fictional scenario: "checkout is slow under load" — what do
   you check first, second, third, and why in that order?
4. Explain why routing a "read your own write" request to a replica is
   risky, and describe two ways to avoid the problem (hint: read-from-
   primary-after-write, or session-level replica lag tracking).

## Common mistakes

- Assuming "PostgreSQL is just better" or "MySQL is just faster" as a
  blanket statement — the right choice depends on workload shape (OLTP vs
  analytical), team familiarity, ecosystem/tooling needs, and existing
  infrastructure. Both are excellent, mature engines.
- Adding a read replica to "fix" a slow database before confirming the
  slowness isn't a single bad query or missing index — replicas add
  operational complexity and don't fix a query that's fundamentally
  inefficient (it'll just be inefficient on more machines).
- Treating monitoring as something to add after an incident rather than
  before — you can't fix what you can't see.

## Production considerations

This entire chapter *is* production considerations — the main one worth
repeating: measure before you optimize, at every level (query, cache,
replication, hardware). Each earlier chapter's "production considerations"
section rolls up into the checklist in `docs/production.md`.
