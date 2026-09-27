# Workflow: Scaling Decision Checklist

Work through in order — don't skip ahead to sharding because it's the
"advanced" answer; it's usually the wrong first answer.

- [ ] Confirmed via `EXPLAIN ANALYZE` that the slow queries have good plans
      (Chapter 3)
- [ ] Confirmed no N+1 query patterns in the ORM layer (Chapter 5)
- [ ] Confirmed connection pooling is configured, not raw per-request
      connections
- [ ] Added caching for the specific hot, expensive, rarely-changing reads
      identified by profiling (Chapter 6) — not caching everything
      speculatively
- [ ] Reviewed indexes for the actual query patterns in production, removed
      unused ones (each index has a write-cost)
- [ ] Only now: considered a read replica for read-heavy load, with a clear
      answer for which requests must read from the primary
- [ ] Only after all the above: considered partitioning/sharding, with a
      concrete partition key chosen based on actual access patterns
