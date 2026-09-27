-- Chapter 3: generate a large synthetic table to make index effects visible.
-- 500k rows is enough for the planner's choices to matter on a laptop.

DROP TABLE IF EXISTS events CASCADE;

CREATE TABLE events (
    id           BIGSERIAL PRIMARY KEY,
    user_id      INTEGER NOT NULL,
    event_type   VARCHAR(30) NOT NULL,
    payload      JSONB,
    created_at   TIMESTAMPTZ NOT NULL
);

INSERT INTO events (user_id, event_type, payload, created_at)
SELECT
    (random() * 10000)::int,                                  -- 10k distinct users
    (ARRAY['click', 'view', 'purchase', 'signup'])[(random()*3+1)::int],
    jsonb_build_object('tag', (ARRAY['sale','new','promo'])[(random()*2+1)::int]),
    now() - (random() * interval '365 days')
FROM generate_series(1, 500000);

ANALYZE events;
