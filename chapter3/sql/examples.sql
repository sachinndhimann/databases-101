-- Chapter 3: EXPLAIN before/after indexing (run setup.sql first)

-- 1. BEFORE: no index on user_id yet -> sequential scan
EXPLAIN ANALYZE SELECT * FROM events WHERE user_id = 42;

-- 2. Add the index
CREATE INDEX idx_events_user_id ON events(user_id);
ANALYZE events;

-- 3. AFTER: same query, should now use Index Scan
EXPLAIN ANALYZE SELECT * FROM events WHERE user_id = 42;

-- 4. Function-on-column defeats the index (BREAK IT)
EXPLAIN ANALYZE SELECT * FROM events WHERE event_type || '' = 'purchase';
-- Seq Scan even though event_type could be indexed, because of the
-- concatenation wrapping the column.

-- 5. Composite index: only helps if leftmost column is constrained
CREATE INDEX idx_events_user_created ON events(user_id, created_at);
ANALYZE events;

EXPLAIN ANALYZE
SELECT * FROM events WHERE user_id = 42 AND created_at > now() - interval '30 days';
-- Index Scan using idx_events_user_created

EXPLAIN ANALYZE
SELECT * FROM events WHERE created_at > now() - interval '30 days';
-- Seq Scan (or a much less effective plan) -- leftmost column not constrained

-- 6. Partial index for a common filtered query
CREATE INDEX idx_events_purchases ON events(user_id) WHERE event_type = 'purchase';
ANALYZE events;

EXPLAIN ANALYZE
SELECT * FROM events WHERE user_id = 42 AND event_type = 'purchase';

-- 7. GIN index for JSONB containment queries
CREATE INDEX idx_events_payload_gin ON events USING GIN (payload);
ANALYZE events;

EXPLAIN ANALYZE
SELECT * FROM events WHERE payload @> '{"tag": "sale"}';
