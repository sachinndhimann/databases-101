-- Chapter 1: working examples to run and observe

-- 1. Basic select with a join (one-to-many: users -> orders)
SELECT u.full_name, o.id AS order_id, o.status, o.created_at
FROM users u
JOIN orders o ON o.user_id = u.id
ORDER BY u.full_name, o.created_at;

-- 2. Order total via the many-to-many junction table (order_items)
SELECT o.id AS order_id, SUM(oi.quantity * oi.unit_price) AS order_total
FROM orders o
JOIN order_items oi ON oi.order_id = o.id
GROUP BY o.id
ORDER BY o.id;

-- 3. Attempt to break a constraint on purpose (BREAK IT)
-- Uncomment and run each one individually to see the exact error:

-- a) violates NOT NULL / FK
-- INSERT INTO orders (user_id, status) VALUES (999, 'pending');
-- ERROR: insert or update on table "orders" violates foreign key constraint

-- b) violates CHECK
-- INSERT INTO products (sku, name, price, stock_qty) VALUES ('SKU-999', 'Broken', -5, 0);
-- ERROR: new row for relation "products" violates check constraint "products_price_check"

-- c) violates UNIQUE
-- INSERT INTO users (email, full_name) VALUES ('sachin@example.com', 'Duplicate Sachin');
-- ERROR: duplicate key value violates unique constraint "users_email_key"

-- 4. ON DELETE CASCADE in action (FIX IT after breaking)
-- Deleting an order removes its order_items and payment automatically:
-- DELETE FROM orders WHERE id = 5;
-- SELECT * FROM order_items WHERE order_id = 5;  -- empty, cascaded

-- 5. A denormalization payoff: unit_price on order_items survives a price change
UPDATE products SET price = 5999.00 WHERE sku = 'SKU-001';
SELECT oi.order_id, oi.unit_price  -- still 4999.00, the price paid at purchase time
FROM order_items oi
JOIN products p ON p.id = oi.product_id
WHERE p.sku = 'SKU-001';
