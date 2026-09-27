# Chapter 1: Exercises

Work these against the seeded schema. Solutions are at the bottom — try
first without looking.

1. Write a query listing every product that has never been ordered.
2. Add a `phone_numbers` capability to `users` without violating 1NF
   (i.e. don't add `phone1`, `phone2` columns). Write the `CREATE TABLE`.
3. A user's order should not be deletable if it has a successful payment.
   Which constraint enforces this today, and does it actually stop the
   delete? Test it, then explain what you'd add (hint: think about
   `ON DELETE` behavior vs. an application-level check vs. a trigger).
4. Identify the normal form violation: a `shipments` table with columns
   `(order_id, product_name, product_category, warehouse_code)`. Which
   normal form is broken and why? Redesign it.
5. **Break it / fix it**: try to insert an `order_items` row with
   `quantity = 0`. Read the exact error message. Now try `quantity = -1`.
   Are both stopped by the same constraint?

## Common mistakes

- Using the row's *position* or a mutable column (like email) as a
  "natural" identifier that other tables reference, instead of a stable
  surrogate primary key. Emails change; a user's identity shouldn't.
- Forgetting `ON DELETE` behavior on foreign keys, leading to either
  orphaned rows (`ON DELETE SET NULL` when you meant `CASCADE`) or
  accidental mass deletes (`CASCADE` when you meant to block the delete
  with `ON DELETE RESTRICT`, the default).
- Adding `UNIQUE` at the application layer only (a "check first, insert
  second" pattern) — this always has a race condition under concurrent
  writes. The database-level `UNIQUE` constraint is the only real guarantee.

## Production considerations

- Every foreign key should have an index on the referencing column (see
  `idx_orders_user_id` etc. in `setup.sql`) — otherwise deletes and updates
  on the referenced table trigger full table scans to check for dependents.
- `CHECK` constraints are cheap insurance but re-verify them during schema
  migrations on very large tables — adding a `CHECK` to an existing large
  Postgres table can require a full table scan unless you use `NOT VALID`
  + `VALIDATE CONSTRAINT` to do it without a long lock (covered in Chapter 7).

## Solutions

<details>
<summary>1. Products never ordered</summary>

```sql
SELECT p.*
FROM products p
LEFT JOIN order_items oi ON oi.product_id = p.id
WHERE oi.id IS NULL;
```
</details>

<details>
<summary>2. Phone numbers, 1NF-compliant</summary>

```sql
CREATE TABLE user_phone_numbers (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    phone_number VARCHAR(20) NOT NULL,
    is_primary BOOLEAN NOT NULL DEFAULT false,
    UNIQUE (user_id, phone_number)
);
```
</details>

<details>
<summary>3. Deleting a paid order</summary>

Today `orders` has no protection — `order_items` and `payments` both use
`ON DELETE CASCADE`, so deleting an order silently deletes its payment too.
Nothing stops it. To actually block this, you'd either: (a) change
`payments.order_id`'s FK to `ON DELETE RESTRICT` (the default if you omit
`ON DELETE`) so the delete errors out while a payment row exists, or (b) add
a `BEFORE DELETE` trigger on `orders` that raises an exception when a
related `payments.status = 'success'` row exists. Prefer (a) — it's
declarative and needs no procedural code.
</details>

<details>
<summary>4. Normal form violation</summary>

3NF violation: `product_category` is transitively dependent on
`product_name`/the product itself, not on the shipment. Redesign:
`shipments(order_id, product_id, warehouse_code)` and look up
`product_category` via a `products` table join.
</details>

<details>
<summary>5. quantity constraint</summary>

Both `0` and `-1` are stopped by the same `CHECK (quantity > 0)` constraint
— the error names `order_items_quantity_check` in both cases.
</details>
