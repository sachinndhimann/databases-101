# Chapter 4: Concepts

## ACID, concretely

- **Atomicity**: a transaction's statements all succeed or all roll back
  together. If step 3 of 5 fails, steps 1-2 are undone too.
- **Consistency**: a transaction moves the database from one valid state to
  another — all constraints (FK, CHECK, UNIQUE) hold before and after.
- **Isolation**: concurrent transactions don't see each other's uncommitted
  changes (to a degree controlled by the isolation level — see below).
- **Durability**: once committed, data survives a crash (via the
  write-ahead log, fsynced to disk).

## Isolation levels and the anomalies they prevent

| Level | Dirty read | Non-repeatable read | Phantom read |
|---|---|---|---|
| Read Uncommitted | Possible | Possible | Possible |
| Read Committed (Postgres/MySQL default*) | Prevented | Possible | Possible |
| Repeatable Read | Prevented | Prevented | Possible (MySQL prevents it too, via gap locks) |
| Serializable | Prevented | Prevented | Prevented |

\* PostgreSQL's default is `READ COMMITTED`. MySQL/InnoDB's default is
`REPEATABLE READ` — this single difference causes real behavioral gaps
when porting an application between the two.

- **Dirty read**: seeing another transaction's *uncommitted* change.
- **Non-repeatable read**: re-reading the same row within one transaction
  gives a different value because another transaction committed a change
  in between.
- **Phantom read**: re-running the same range query within one transaction
  returns a different *set of rows* (new rows appeared or vanished).

Higher isolation costs more: `SERIALIZABLE` in Postgres works by detecting
conflicts and aborting one of the conflicting transactions (you must be
prepared to retry on a serialization failure), not by locking everything
upfront.

## Row locking

```sql
BEGIN;
SELECT * FROM products WHERE id = 1 FOR UPDATE;  -- locks this row
UPDATE products SET stock_qty = stock_qty - 1 WHERE id = 1;
COMMIT;
```

`FOR UPDATE` takes a row-level lock so a second concurrent transaction
trying to do the same thing blocks until the first commits — this is how
you prevent a lost update (two transactions both reading `stock_qty = 5`,
both decrementing, and the final value being 4 instead of 3).

## Deadlocks

A deadlock happens when transaction A holds a lock transaction B wants,
and B holds a lock A wants — neither can proceed. Both Postgres and MySQL
detect this automatically and abort one transaction (the "deadlock
victim") with an error, letting the other proceed. The fix is
application-level: always acquire locks on multiple rows **in the same
order** across all code paths (e.g. always lock the lower `id` first).

## PostgreSQL vs MySQL

| Aspect | PostgreSQL | MySQL (InnoDB) |
|---|---|---|
| Default isolation | READ COMMITTED | REPEATABLE READ |
| MVCC implementation | Old row versions kept in the table itself, cleaned by VACUUM | Old versions kept in the undo log |
| Phantom prevention at REPEATABLE READ | Not fully prevented (only SERIALIZABLE prevents it) | Prevented via next-key (gap) locks |
| Serializable implementation | Optimistic — detects conflicts, aborts on commit (SSI) | Pessimistic — locks proactively |
