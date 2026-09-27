# Production Considerations — cross-chapter summary

## Backups

- **Logical backups** (`pg_dump` / `mysqldump`): portable, human-readable
  SQL, but slow to restore for large databases and lock-free but not
  point-in-time consistent by default (`pg_dump` *is* transactionally
  consistent via a single snapshot; `mysqldump` needs
  `--single-transaction` for InnoDB to get the same guarantee).
- **Physical backups** (`pg_basebackup`, Percona XtraBackup): copy the raw
  data files, much faster restore, but tied to the same major version and
  architecture.
- **Point-in-time recovery (PITR)**: combine a physical base backup with
  continuously archived write-ahead logs (Postgres WAL, MySQL binlog) so
  you can restore to any specific second, not just the last backup time.
- Test restores regularly — an untested backup is a belief, not a backup.

## Monitoring

Track, at minimum:
- Query latency percentiles (p50/p95/p99), not just averages.
- Connection count vs. max connections (connection exhaustion is a common
  outage cause).
- Replication lag, if you run replicas.
- Cache hit ratio (both the database's own buffer cache and any
  application-level Redis cache).
- Lock waits / deadlock counts.
- Disk usage growth rate (a slow leak in WAL/binlog retention or table
  bloat is often invisible until it isn't).

Tools: `pg_stat_statements` and `pg_stat_activity` (Postgres), the
Performance Schema (MySQL), plus a metrics pipeline (Prometheus exporters
for both engines are mature and standard) feeding dashboards and alerts.

## Replication & read replicas

- Both engines support asynchronous streaming replication out of the box.
- Read replicas offload read traffic from the primary, but replication lag
  means a replica can serve stale data — never route a read-after-write
  request (e.g. "show the order I just placed") to a replica without
  accounting for this.
- Failover (promoting a replica to primary) is not automatic in either
  engine's core — use a tool built for it (Patroni for Postgres,
  Orchestrator/group replication for MySQL) rather than hand-rolling it.

## Scaling patterns

1. **Vertical scaling**: bigger instance. Simplest, has a ceiling, and
   downtime during resize unless your infra supports live resize.
2. **Read replicas**: scale read throughput horizontally; writes still go
   through one primary.
3. **Connection pooling** (PgBouncer, ProxySQL): databases have a hard
   limit on concurrent connections; an app with hundreds of workers each
   opening a direct connection will exhaust it. A pooler multiplexes many
   app-level connections onto fewer real database connections.
4. **Partitioning/sharding**: split one logical table across multiple
   physical tables (partitioning, same database) or multiple database
   instances entirely (sharding). Sharding is a major complexity jump —
   exhaust the simpler options first.
5. **Caching** (Chapter 6): often the highest-leverage change before
   touching the database topology at all.

## A pragmatic order of operations when a database is "slow"

1. Confirm it's actually the database (check APM/tracing) before assuming.
2. `EXPLAIN ANALYZE` the specific slow query (Chapter 3).
3. Check for missing/wrong indexes, stale statistics, N+1 queries
   (Chapter 5).
4. Check connection pool exhaustion and lock waits (Chapter 4).
5. Only then consider caching, replicas, or hardware — after confirming the
   query itself is sound; caching a bad query just hides the problem.
