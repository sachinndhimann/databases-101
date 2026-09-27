# Chapter 5: Exercises

1. Run `n_plus_one_demo.py` and count the actual `SELECT` statements printed
   in each section. Confirm it's `1 + N` in the first section and `1` in
   the second.
2. Add a `Payment` model (one-to-one with `Order`) and write a query that
   eager-loads both `Order.user` and `Order.payment` in a single round trip.
3. Write a bulk insert of 1,000 `Product` rows using SQLAlemy Core
   (`session.execute(insert(Product), [...])`) and compare its speed to
   creating 1,000 ORM objects and adding them one by one via `session.add()`.
4. Deliberately cause a `DetachedInstanceError`: load an `Order`, close the
   session, then try to access `order.user`. Explain why it fails and how
   eager loading before closing the session avoids it.

## Common mistakes

- Accessing a lazy relationship inside a loop (`for order in orders:
  order.user.full_name`) — the classic N+1. Not visible with 3 test rows;
  crushing with 30,000 production rows.
- Calling `session.commit()` inside a loop when a single commit at the end
  would do — each commit is a round trip and (depending on settings) an
  fsync.
- Treating ORM objects as valid forever. Once a `Session` is closed, lazy
  attributes on its objects can no longer load — this is a *feature*
  (it stops you from accidentally hitting the database from stale objects),
  not a bug to work around with global sessions.

## Production considerations

- Turn on `echo=True` (or a SQL logging middleware) in staging, never
  silently trust that the ORM is doing something efficient — verify it.
- Use `selectinload` over `joinedload` for one-to-many relationships with
  many children — a `joinedload` duplicates the parent row once per child
  in the result set before SQLAlchemy de-duplicates it in Python, which
  wastes network bandwidth at scale.
- Connection pooling matters as much as query efficiency: configure
  `pool_size`/`max_overflow` on `create_engine()` deliberately rather than
  relying on defaults, especially behind a web framework with many workers.
