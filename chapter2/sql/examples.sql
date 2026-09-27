-- Chapter 2: SQL deep dive examples (run after chapter1 setup.sql + seed.sql)

-- 1. All join types side by side
SELECT u.full_name, o.id AS order_id
FROM users u INNER JOIN orders o ON o.user_id = u.id;

SELECT u.full_name, o.id AS order_id
FROM users u LEFT JOIN orders o ON o.user_id = u.id;   -- includes users with no orders

-- Postgres has no FULL OUTER support gap, but MySQL does — Postgres version:
SELECT u.full_name, o.id AS order_id
FROM users u FULL OUTER JOIN orders o ON o.user_id = u.id;

-- 2. Correlated subquery: users who have placed at least one order
SELECT full_name FROM users u
WHERE EXISTS (SELECT 1 FROM orders o WHERE o.user_id = u.id);

-- 3. NOT IN vs NOT EXISTS trap: users who have NEVER ordered
-- Dangerous if orders.user_id could ever be NULL (it can't here due to NOT NULL,
-- but this is the classic bug to know about):
SELECT full_name FROM users u
WHERE u.id NOT IN (SELECT user_id FROM orders WHERE user_id IS NOT NULL);

-- Safer, always-correct form:
SELECT full_name FROM users u
WHERE NOT EXISTS (SELECT 1 FROM orders o WHERE o.user_id = u.id);

-- 4. CTE: order totals, then filter on the CTE result (can't filter an
-- aggregate directly in WHERE without a CTE or subquery/HAVING)
WITH order_totals AS (
    SELECT o.id AS order_id, o.user_id, SUM(oi.quantity * oi.unit_price) AS total
    FROM orders o JOIN order_items oi ON oi.order_id = o.id
    GROUP BY o.id, o.user_id
)
SELECT u.full_name, ot.order_id, ot.total
FROM order_totals ot JOIN users u ON u.id = ot.user_id
WHERE ot.total > 10000
ORDER BY ot.total DESC;

-- 5. Recursive CTE example (generic, using a generated series as a stand-in
-- hierarchy since this schema has no self-referencing table)
WITH RECURSIVE countdown(n) AS (
    SELECT 5
    UNION ALL
    SELECT n - 1 FROM countdown WHERE n > 1
)
SELECT n FROM countdown;

-- 6. Window functions: rank each user's orders by recency, running spend
WITH order_totals AS (
    SELECT o.id AS order_id, o.user_id, o.created_at,
           SUM(oi.quantity * oi.unit_price) AS total
    FROM orders o JOIN order_items oi ON oi.order_id = o.id
    GROUP BY o.id, o.user_id, o.created_at
)
SELECT
    user_id, order_id, total,
    ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY created_at) AS order_seq,
    SUM(total) OVER (PARTITION BY user_id ORDER BY created_at) AS running_total,
    LAG(total) OVER (PARTITION BY user_id ORDER BY created_at) AS previous_order_total
FROM order_totals
ORDER BY user_id, created_at;
