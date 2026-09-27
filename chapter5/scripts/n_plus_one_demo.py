"""
Chapter 5: demonstrate the N+1 query problem, then fix it.
Watch the SQL echo output — count the SELECT statements in each section.
"""
from sqlalchemy.orm import Session, joinedload

from models import Order, get_engine


def run_n_plus_one(session):
    print("\n=== N+1 (lazy loading, one query per order) ===")
    orders = session.query(Order).all()          # query 1
    for order in orders:
        _ = order.user.full_name                 # query 2..N+1


def run_fixed(session):
    print("\n=== FIXED (joinedload — single query with JOIN) ===")
    orders = session.query(Order).options(joinedload(Order.user)).all()  # 1 query total
    for order in orders:
        _ = order.user.full_name                 # no additional query, already loaded


def main():
    engine = get_engine(echo=True)  # echo=True prints every SQL statement executed
    with Session(engine) as session:
        run_n_plus_one(session)
        session.expunge_all()  # clear identity map so the fixed version isn't cheating
        run_fixed(session)


if __name__ == "__main__":
    main()
