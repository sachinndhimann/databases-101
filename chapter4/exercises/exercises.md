# Chapter 4: Exercises

1. Run `race_condition_demo.py` five times. Does it reproduce the lost
   update every time? Why might timing-dependent bugs like this pass in
   testing and fail in production?
2. Modify `fixed_with_locking.py` to intentionally create a deadlock: have
   two threads lock two different products in opposite order
   (`thread1: lock product 1 then 2`, `thread2: lock product 2 then 1`).
   Observe Postgres's deadlock detection error.
3. Set the isolation level to `SERIALIZABLE` on both connections in the
   race condition demo (no `FOR UPDATE`) and see if Postgres's optimistic
   conflict detection also prevents the lost update (one transaction should
   fail with a serialization error — you'll need to catch and retry it).
4. Explain, in your own words, why `REPEATABLE READ` alone (without
   `FOR UPDATE` or `SERIALIZABLE`) does NOT prevent the lost update in this
   demo, even though it prevents non-repeatable reads.

## Common mistakes

- Read-then-write application logic (read a value, compute in app code,
  write it back) without a lock or an atomic `UPDATE ... SET x = x - 1` —
  this is the #1 source of lost updates in real applications.
- Assuming `REPEATABLE READ` means "no other transaction can interfere."
  It stops *your* reads from changing mid-transaction; it does not
  automatically make a read-modify-write cycle safe.
- Holding a `FOR UPDATE` lock across a slow operation (an external API
  call, a long computation) inside the transaction — this serializes all
  concurrent buyers behind that slow call. Keep locked transactions short.

## Production considerations

- Prefer atomic single-statement updates (`UPDATE products SET stock_qty =
  stock_qty - 1 WHERE id = ? AND stock_qty > 0 RETURNING stock_qty`) over
  read-then-write-with-lock wherever possible — no lock needed, no deadlock
  risk, and it's simpler.
- Always have retry logic around `SERIALIZABLE` transactions — they are
  *expected* to fail sometimes under contention; that's how the isolation
  level works.
- Monitor for deadlocks in production logs (`log_lock_waits` in Postgres) —
  frequent deadlocks indicate a real lock-ordering bug, not bad luck.
