# Chapter 5: Concepts

## Core vs ORM

- **SQLAlchemy Core**: you build SQL expressions in Python
  (`select(users).where(...)`) and get back plain rows. Closer to raw SQL —
  full control, less "magic."
- **SQLAlchemy ORM**: you define Python classes mapped to tables
  (`class User(Base): ...`) and work with objects. The ORM tracks changes to
  those objects and generates the SQL for you.

Use Core for bulk operations, reporting queries, or anything performance
critical where you want to see exactly what SQL runs. Use the ORM for
typical CRUD-heavy application code where object-oriented modeling pays off.

## Declarative models and relationships

```python
class User(Base):
    __tablename__ = "users"
    id = mapped_column(Integer, primary_key=True)
    email = mapped_column(String(255), unique=True, nullable=False)
    orders = relationship("Order", back_populates="user")

class Order(Base):
    __tablename__ = "orders"
    id = mapped_column(Integer, primary_key=True)
    user_id = mapped_column(ForeignKey("users.id"))
    user = relationship("User", back_populates="orders")
```

`relationship()` doesn't create a database column — it's a Python-side
convenience that tells SQLAlchemy how to load related objects, based on
the actual foreign key.

## Sessions and the unit of work

A `Session` is not a database connection — it's a staging area. Changes to
mapped objects are tracked in memory; `session.flush()` sends pending SQL
to the database (but doesn't commit the transaction); `session.commit()`
flushes and commits. This means you can make several changes across many
objects and have them go out as one atomic transaction.

```python
with Session(engine) as session:
    user = session.get(User, 1)
    user.full_name = "New Name"   # tracked, not yet sent
    session.commit()               # NOW the UPDATE is sent and committed
```

## The N+1 problem

```python
orders = session.query(Order).all()          # 1 query
for order in orders:
    print(order.user.full_name)              # N additional queries — one per order!
```

Each `order.user` access lazily fires its own `SELECT` unless you tell
SQLAlchemy to load it eagerly:

```python
from sqlalchemy.orm import joinedload, selectinload

# joinedload: one query with a JOIN (good for to-one relationships)
orders = session.query(Order).options(joinedload(Order.user)).all()

# selectinload: two queries total, second one is "WHERE id IN (...)"
# (good for to-many relationships, avoids a duplicated result set from a JOIN)
users = session.query(User).options(selectinload(User.orders)).all()
```

This is the single most common ORM performance bug in production systems —
it's invisible in development with 5 rows and catastrophic in production
with 50,000.

## PostgreSQL vs MySQL in SQLAlchemy

| Aspect | PostgreSQL | MySQL |
|---|---|---|
| Driver | `psycopg2` or `psycopg` (v3) | `PyMySQL` or `mysqlclient` |
| URL scheme | `postgresql+psycopg2://` | `mysql+pymysql://` |
| Native `RETURNING` | Yes — SQLAlchemy uses it for efficient bulk inserts | No — SQLAlchemy falls back to a second round-trip for `inserted_primary_key` |
| `JSONB` type | `sqlalchemy.dialects.postgresql.JSONB` | Use generic `JSON` type, no binary variant |
