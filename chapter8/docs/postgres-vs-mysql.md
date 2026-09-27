# PostgreSQL vs MySQL — full comparison

## Data types

| Type | PostgreSQL | MySQL |
|---|---|---|
| Boolean | Native `BOOLEAN` | `TINYINT(1)` convention, no real boolean before 8.0's alias |
| Arrays | Native array types (`INTEGER[]`) | No native array type |
| JSON | `JSON` (text) and `JSONB` (binary, indexable) | `JSON` only (stored as binary internally since 5.7, but one type) |
| UUID | Native `UUID` type | `CHAR(36)` or `BINARY(16)` convention |
| Enum | `CREATE TYPE ... AS ENUM` | `ENUM` column type (simpler, but harder to alter later) |

## Constraints

- PostgreSQL enforces `CHECK` constraints unconditionally.
- MySQL only enforces `CHECK` since 8.0.16 — earlier versions parse but
  silently ignore them. Always verify the MySQL version before relying on
  `CHECK` for correctness.

## Indexes

- Both support B-tree as the default.
- PostgreSQL additionally offers GIN (full text, JSONB, arrays), GiST
  (geometric/range types), BRIN (very large, naturally-ordered tables like
  time-series).
- MySQL (InnoDB) tables are **clustered** on the primary key — the table
  data itself is stored in primary-key order. A secondary index lookup in
  MySQL requires two B-tree traversals (secondary index -> primary key ->
  row). PostgreSQL's heap tables mean every index, including the primary
  key's, points directly at a heap location (TID) in one hop, but heap
  tables can become fragmented (`VACUUM` cleans this).

## Transactions & isolation levels

- Default isolation: PostgreSQL `READ COMMITTED`; MySQL/InnoDB
  `REPEATABLE READ`.
- MySQL's `REPEATABLE READ` also prevents phantom reads via gap locking —
  stricter than the SQL standard requires at that level. PostgreSQL's
  `REPEATABLE READ` does not prevent phantoms; only `SERIALIZABLE` does.

## JSON support

- PostgreSQL `JSONB`: binary storage, supports GIN indexing and
  containment operators (`@>`, `?`, `#>`). Generally the better choice when
  you need to *query* inside JSON regularly.
- MySQL `JSON`: also binary-stored internally, supports functional indexes
  via generated columns (`col->>'$.key'` as a stored generated column, then
  index that column) but less flexible containment querying.

## Upserts

```sql
-- PostgreSQL
INSERT INTO products (sku, price) VALUES ('SKU-1', 10)
ON CONFLICT (sku) DO UPDATE SET price = EXCLUDED.price;

-- MySQL
INSERT INTO products (sku, price) VALUES ('SKU-1', 10)
ON DUPLICATE KEY UPDATE price = VALUES(price);
```
Semantically similar, syntactically different keywords.

## Full-text search

- PostgreSQL: `tsvector`/`tsquery` + GIN index, built-in and flexible,
  language-aware stemming via configurable dictionaries.
- MySQL: `FULLTEXT` indexes (InnoDB since 5.6), simpler API, generally
  considered less powerful/flexible for complex ranking or multi-language
  needs; many teams reach for Elasticsearch/OpenSearch once needs grow
  regardless of which relational engine they use.

## Locking

- PostgreSQL: MVCC with old row versions kept in the table itself, cleaned
  up by `VACUUM`/autovacuum (a table that never gets vacuumed can bloat).
- MySQL/InnoDB: MVCC with old versions kept in a separate undo log,
  reclaimed automatically; also uses gap/next-key locking under
  `REPEATABLE READ` that PostgreSQL doesn't have an equivalent for.

## Query planners

- PostgreSQL's planner is cost-based with detailed statistics
  (histograms, most-common-values lists) and generally considered more
  sophisticated for complex analytical queries.
- MySQL's optimizer has improved significantly since 8.0 (histograms,
  better join ordering, CTEs, window functions) but historically lagged
  Postgres on complex multi-join analytical queries; it remains extremely
  strong for high-throughput simple OLTP lookups.

## Auto-increment / sequences

- PostgreSQL: `SERIAL`/`IDENTITY` are backed by independent `SEQUENCE`
  objects you can share, reset, or query directly (`nextval`, `currval`).
- MySQL: `AUTO_INCREMENT` is a table-level property, simpler but less
  flexible (can't easily share one counter across tables, for instance).

## Date/time handling

- PostgreSQL: `TIMESTAMPTZ` stores an instant, always normalized to UTC
  internally, displayed in the session's timezone — this is almost always
  what you want for application timestamps.
- MySQL: `TIMESTAMP` also converts to/from the session's `time_zone`, but
  has a narrower range (1970-2038 on some configurations) and different
  behavior on the "zero date" `0000-00-00`. `DATETIME` stores no timezone
  info at all — genuinely ambiguous once your application spans time zones.

## NULL behavior

Standard SQL three-valued logic applies in both engines. The practical
difference is more about tooling and defaults: MySQL historically allowed
more implicit type coercion in comparisons, which can produce
surprising results with `NULL` and non-strict SQL modes — always run
current MySQL with `sql_mode=STRICT_TRANS_TABLES` (default since 5.7) to
avoid silent data truncation.

## Generated columns / views / materialized views

- Both support `VIEW`.
- PostgreSQL: native `MATERIALIZED VIEW` with manual/scheduled
  `REFRESH MATERIALIZED VIEW`.
- MySQL: no native materialized view — emulate with a real table plus a
  scheduled event or external job that repopulates it.
- Both support generated/computed columns (`GENERATED ALWAYS AS (...)`),
  syntax differs slightly.
