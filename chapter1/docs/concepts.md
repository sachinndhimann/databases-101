# Chapter 1: Concepts

## 1. What is a relational database?

A relational database stores data as **tables** (relations) — grids of rows
and columns — and lets you query across tables by matching values, not by
following pre-built pointers (that's the older network/hierarchical model).
The engine guarantees:

- **Structure**: every row in a table has the same columns.
- **Integrity**: constraints stop bad data from being written in the first place.
- **Consistency across tables**: foreign keys enforce that a reference points
  to something that actually exists.

## 2. Tables, rows, columns

- **Table**: a named collection of rows with a fixed set of typed columns (e.g. `users`).
- **Row** (tuple): one record — `(1, 'sachin@example.com', 'Sachin', ...)`.
- **Column** (attribute): a named, typed field — `email VARCHAR(255)`.

## 3. Keys

- **Primary key**: uniquely identifies a row. A table has exactly one. Cannot be NULL.
- **Candidate key**: any column set that *could* serve as the primary key
  (unique + not null). A table may have several; the rest usually become
  UNIQUE constraints.
- **Foreign key**: a column referencing another table's primary key, enforcing
  that the referenced row exists.

```sql
id SERIAL PRIMARY KEY                        -- primary key
email VARCHAR(255) UNIQUE NOT NULL           -- candidate key as UNIQUE constraint
user_id INTEGER REFERENCES users(id)         -- foreign key
```

## 4. Constraints

| Constraint | Purpose | Example |
|---|---|---|
| `NOT NULL` | column must always have a value | `name TEXT NOT NULL` |
| `UNIQUE` | no two rows share this value | `email TEXT UNIQUE` |
| `CHECK` | value must satisfy a boolean expression | `CHECK (price >= 0)` |
| `DEFAULT` | value used when none is supplied | `status TEXT DEFAULT 'pending'` |
| `FOREIGN KEY` | value must exist in another table | `REFERENCES orders(id)` |
| `PRIMARY KEY` | unique + not null, identifies the row | `id SERIAL PRIMARY KEY` |

Constraints are the cheapest bugs you'll ever prevent. A `CHECK (price >= 0)`
costs nothing at write time and saves you a 3am page when a negative price
breaks a billing job.

## 5. Relationships

- **One-to-many**: one `users` row → many `orders` rows, via `orders.user_id`.
- **Many-to-many**: many `orders` ↔ many `products`, via a **junction table**
  (`order_items`) holding a foreign key to each side plus its own attributes
  (`quantity`, `unit_price`).
- **One-to-one**: one `orders` row → at most one `payments` row, via a unique
  foreign key (or making the foreign key itself the child's primary key).

## 6. Normalization

- **1NF**: every column holds a single atomic value; no repeating groups.
  (`phone1, phone2, phone3` columns violate this — use a child table.)
- **2NF**: 1NF, plus every non-key column depends on the *whole* primary key,
  not just part of it. Only matters for composite primary keys.
- **3NF**: 2NF, plus no non-key column depends on another non-key column.
  Example violation: storing `product_id` and `product_category_name` on
  `order_items` — category name depends on `product_id`, not the order line.

### When normalization becomes counterproductive

Strict normalization optimizes for write integrity, not read speed. You
denormalize (intentionally duplicate data) when:

- A join is on a documented hot path and profiling shows it's the
  bottleneck — e.g. duplicating `product_name` onto `order_items` so a
  historical order doesn't change if the product is renamed later (this is
  actually more *correct*, not just faster).
- You're building read-heavy reporting tables / materialized views refreshed
  on a schedule, kept separate from the normalized transactional tables.
- Analytical (OLAP) workloads: star/snowflake schemas denormalize dimensions
  on purpose for query simplicity.

Rule of thumb: normalize for correctness first, then denormalize
deliberately and measurably for read performance.

## PostgreSQL vs MySQL — Chapter 1 relevant differences

| Aspect | PostgreSQL | MySQL |
|---|---|---|
| Auto-increment | `SERIAL` / `GENERATED ALWAYS AS IDENTITY` | `AUTO_INCREMENT` |
| Boolean type | Native `BOOLEAN` | No native type; stored as `TINYINT(1)` |
| Identifier case | Case-sensitive if quoted, folds to lowercase otherwise | Table name case-sensitivity depends on OS/filesystem |
| Storage engine | Single built-in engine | Pluggable — almost always InnoDB today |
| CHECK constraint | Always enforced | Only enforced since 8.0.16 (silently ignored before) |
