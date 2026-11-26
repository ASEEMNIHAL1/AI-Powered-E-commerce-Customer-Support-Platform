"""
Seed script – creates deterministic demo data.
Run: python seed.py

Demo credentials:
  Customer 1: alice@example.com / password123
  Customer 2: bob@example.com / password123
  Staff:      staff@shopeasy.com / staffpass123
"""
import os
import sys
from datetime import date, datetime, timezone, timedelta

# Allow running from backend/ dir
sys.path.insert(0, os.path.dirname(__file__))

from app.db.session import SessionLocal, engine
from app.db.base import Base
import app.models  # noqa: F401
from app.models.user import User, UserRole
from app.models.order import Order, OrderStatus, ItemCategory
from app.core.security import hash_password


def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # Idempotent: skip if already seeded
        if db.query(User).count() > 0:
            print("Database already seeded. Skipping.")
            return

        today = date.today()

        # Users
        alice = User(name="Alice Kumar", email="alice@example.com",
                     hashed_password=hash_password("password123"), role=UserRole.CUSTOMER)
        bob = User(name="Bob Sharma", email="bob@example.com",
                   hashed_password=hash_password("password123"), role=UserRole.CUSTOMER)
        staff = User(name="Support Staff", email="staff@shopeasy.com",
                     hashed_password=hash_password("staffpass123"), role=UserRole.STAFF)
        admin = User(name="Admin User", email="admin@shopeasy.com",
                     hashed_password=hash_password("adminpass123"), role=UserRole.ADMIN)
        db.add_all([alice, bob, staff, admin])
        db.flush()

        # Orders for Alice
        orders_alice = [
            Order(customer_id=alice.id, status=OrderStatus.DELIVERED, item_name="Samsung Galaxy S24",
                  category=ItemCategory.ELECTRONICS, total_amount_paise=7999900,
                  delivery_date=today - timedelta(days=5)),
            Order(customer_id=alice.id, status=OrderStatus.DELIVERED, item_name="Blue Denim Jeans",
                  category=ItemCategory.CLOTHING, total_amount_paise=299900,
                  delivery_date=today - timedelta(days=3)),
            Order(customer_id=alice.id, status=OrderStatus.DELIVERED, item_name="Python Cookbook",
                  category=ItemCategory.BOOKS, total_amount_paise=89900,
                  delivery_date=today - timedelta(days=20)),
            Order(customer_id=alice.id, status=OrderStatus.DELIVERED, item_name="USB-C Hub",
                  category=ItemCategory.ELECTRONICS, total_amount_paise=349900,
                  delivery_date=today - timedelta(days=45)),  # expired return window
            Order(customer_id=alice.id, status=OrderStatus.SHIPPED, item_name="Coffee Maker",
                  category=ItemCategory.HOME, total_amount_paise=499900, delivery_date=None),
            Order(customer_id=alice.id, status=OrderStatus.DELIVERED, item_name="Wireless Earbuds",
                  category=ItemCategory.ELECTRONICS, total_amount_paise=199900,
                  delivery_date=today - timedelta(days=10)),
        ]
        # Orders for Bob
        orders_bob = [
            Order(customer_id=bob.id, status=OrderStatus.DELIVERED, item_name="MacBook Air M3",
                  category=ItemCategory.ELECTRONICS, total_amount_paise=11999900,
                  delivery_date=today - timedelta(days=2)),
            Order(customer_id=bob.id, status=OrderStatus.DELIVERED, item_name="Running Shoes",
                  category=ItemCategory.CLOTHING, total_amount_paise=499900,
                  delivery_date=today - timedelta(days=8)),
            Order(customer_id=bob.id, status=OrderStatus.PENDING, item_name="Instant Noodles Pack",
                  category=ItemCategory.FOOD, total_amount_paise=19900, delivery_date=None),
            Order(customer_id=bob.id, status=OrderStatus.DELIVERED, item_name="Table Lamp",
                  category=ItemCategory.HOME, total_amount_paise=129900,
                  delivery_date=today - timedelta(days=1)),
        ]
        db.add_all(orders_alice + orders_bob)
        db.commit()

        print("✅ Seed complete!")
        print("Demo accounts:")
        print("  Customer: alice@example.com / password123")
        print("  Customer: bob@example.com / password123")
        print("  Staff:    staff@shopeasy.com / staffpass123")
        print("  Admin:    admin@shopeasy.com / adminpass123")

    finally:
        db.close()


if __name__ == "__main__":
    seed()
