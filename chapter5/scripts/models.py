"""Chapter 5: SQLAlchemy declarative models mapped onto the Chapter 1 schema."""
import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import ForeignKey, Numeric, String, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

load_dotenv(Path(__file__).resolve().parents[2] / ".env")


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True)
    full_name: Mapped[str] = mapped_column(String(200))
    orders: Mapped[list["Order"]] = relationship(back_populates="user")


class Order(Base):
    __tablename__ = "orders"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    status: Mapped[str] = mapped_column(String(20))
    user: Mapped["User"] = relationship(back_populates="orders")
    items: Mapped[list["OrderItem"]] = relationship(back_populates="order")


class Product(Base):
    __tablename__ = "products"
    id: Mapped[int] = mapped_column(primary_key=True)
    sku: Mapped[str] = mapped_column(String(64), unique=True)
    name: Mapped[str] = mapped_column(String(200))
    price: Mapped[float] = mapped_column(Numeric(10, 2))


class OrderItem(Base):
    __tablename__ = "order_items"
    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"))
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    quantity: Mapped[int]
    unit_price: Mapped[float] = mapped_column(Numeric(10, 2))
    order: Mapped["Order"] = relationship(back_populates="items")


def get_engine(echo=False):
    url = os.getenv(
        "POSTGRES_URL",
        "postgresql+psycopg2://db101:db101pass@localhost:5432/db101",
    )
    return create_engine(url, echo=echo)


if __name__ == "__main__":
    engine = get_engine(echo=True)
    print("Models defined. Tables map onto the existing chapter1 schema:")
    for table in Base.metadata.tables:
        print(f"  - {table}")
