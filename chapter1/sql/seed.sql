-- Chapter 1: realistic sample data

INSERT INTO users (email, full_name) VALUES
    ('sachin@example.com', 'Sachin Dhiman'),
    ('priya@example.com', 'Priya Sharma'),
    ('rahul@example.com', 'Rahul Verma'),
    ('ananya@example.com', 'Ananya Iyer');

INSERT INTO products (sku, name, price, stock_qty) VALUES
    ('SKU-001', 'Mechanical Keyboard', 4999.00, 50),
    ('SKU-002', '27-inch Monitor', 15999.00, 20),
    ('SKU-003', 'USB-C Dock', 3499.00, 100),
    ('SKU-004', 'Ergonomic Mouse', 1999.00, 75),
    ('SKU-005', 'Standing Desk', 22999.00, 10);

INSERT INTO orders (user_id, status) VALUES
    (1, 'paid'),
    (1, 'shipped'),
    (2, 'pending'),
    (3, 'cancelled'),
    (4, 'paid');

INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES
    (1, 1, 1, 4999.00),
    (1, 4, 2, 1999.00),
    (2, 5, 1, 22999.00),
    (3, 2, 1, 15999.00),
    (3, 3, 1, 3499.00),
    (5, 1, 1, 4999.00),
    (5, 3, 3, 3499.00);

INSERT INTO payments (order_id, amount, method, status, paid_at) VALUES
    (1, 8997.00, 'card', 'success', now() - interval '3 days'),
    (2, 22999.00, 'upi', 'success', now() - interval '1 day'),
    (5, 15496.00, 'card', 'success', now());
