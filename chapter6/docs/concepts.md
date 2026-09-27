# Chapter 6: Concepts

## Cache-aside (the pattern you'll use 90% of the time)

```
READ:
  1. Check cache for key.
  2. Hit?  Return cached value.
  3. Miss? Query the database, store result in cache with a TTL, return it.

WRITE:
  1. Write to the database.
  2. Invalidate (delete) the cache key — don't try to update it in place;
     deleting is simpler and avoids races between two concurrent writers.
```

Redis never talks to the database directly in this pattern — your
application code is the one deciding when to read/write which store. This
is why it's called "aside": the cache sits *beside* the data flow, not
inside it.

## Write-through vs write-behind (less common, know they exist)

- **Write-through**: every write goes to the cache and the database
  synchronously, in the same request. Cache is always fresh, but write
  latency includes both stores.
- **Write-behind (write-back)**: write to the cache immediately, flush to
  the database asynchronously later. Fast writes, but risks data loss if
  the cache crashes before the flush — rarely worth the complexity outside
  specialized systems.

## TTLs and invalidation

> "There are only two hard things in computer science: cache invalidation,
> naming things, and off-by-one errors." — attributed to Phil Karlton

- A **TTL (time-to-live)** bounds how long stale data can be served, even
  if you forget to invalidate explicitly. Always set one — an unbounded
  cache entry is a bug waiting to surface.
- **Explicit invalidation** (deleting the key on write) keeps data fresher
  than relying on TTL alone, but only works if every code path that writes
  the underlying data also remembers to invalidate — a common source of
  bugs when multiple services can write the same data.
- For data that changes rarely but must never be stale for long (pricing,
  inventory), use a short TTL (seconds) combined with explicit invalidation
  as a belt-and-braces approach.

## Cache stampede ("thundering herd")

When a hot key expires, many concurrent requests can all miss the cache at
the same instant and all hammer the database simultaneously to
recompute the same value.

Mitigations:
1. **Lock/single-flight**: the first request to miss acquires a short-lived
   lock and recomputes; others wait briefly and then retry the cache.
2. **Probabilistic early expiration**: recompute *slightly before* the TTL
   expires, with a small random jitter, so not all instances expire at
   exactly the same second.
3. **Stale-while-revalidate**: serve the (slightly) stale value immediately
   while one request refreshes it in the background.

## Redis beyond caching

- **Rate limiting**: `INCR` + `EXPIRE` on a key per user per time window is
  a simple, fast fixed-window limiter.
- **Counters**: atomic `INCR`/`DECR` avoid the same lost-update race
  discussed in Chapter 4, without needing a database transaction.
- **Leaderboards**: Redis Sorted Sets (`ZADD`, `ZRANGE`) give O(log n)
  ranked inserts and range queries for free.

## When NOT to cache

- Data that changes on every read anyway (no benefit).
- Data where staleness is actually dangerous (e.g. a real-time available
  seat count for the very last seat) unless paired with a strict
  invalidation guarantee.
- Premature optimization — profile first. Caching adds a second source of
  truth and a new class of bugs; only pay that cost where it's measured to
  matter.
