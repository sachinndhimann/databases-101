# Chapter 6: Exercises

1. Run `stampede_demo.py`. Confirm the unprotected version shows close to
   20 expensive recomputes while the single-flight version shows close to 1.
2. Add probabilistic early expiration to `cache_aside_demo.py`: store an
   `expires_at` timestamp alongside the cached value, and if a read happens
   within a random window before the real expiry, treat it as a soft miss
   and refresh in the background (in this simple sync demo, just recompute
   synchronously, but note where you'd hand off to a background worker).
3. Implement a fixed-window rate limiter with `INCR` + `EXPIRE`: allow at
   most 5 requests per user per 10-second window; reject the 6th.
4. Explain in your own words why `DEL` on write is generally safer than
   trying to `SET` the cache directly to the new value on write, in a
   system with more than one writer.

## Common mistakes

- No TTL at all — an entry that's never invalidated correctly becomes
  permanently stale the moment a bug slips through one write path.
- Caching error responses / empty results without a short TTL — a
  temporary database hiccup can get "cached" as the permanent answer.
- Using the cache as the source of truth for anything that must survive a
  cache flush (Redis restarts, evictions under memory pressure). Redis
  used as a cache should always be reconstructable from the database.

## Production considerations

- Set `maxmemory-policy` deliberately (e.g. `allkeys-lru`) — the default
  can be `noeviction`, which makes Redis start rejecting writes once full,
  rather than evicting old cache entries.
- Namespace cache keys by version (`product:v2:123`) so a schema/format
  change can be rolled out without needing to explicitly flush the entire
  cache — old-format keys just age out via TTL.
- Watch cache hit ratio in production, not just latency — a "fast" cache
  layer with a 20% hit rate is mostly just extra complexity and network
  hops for little benefit.
