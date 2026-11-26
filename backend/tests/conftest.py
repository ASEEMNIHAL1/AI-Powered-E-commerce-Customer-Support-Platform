"""Shared test fixtures and in-memory SQLite database."""
import os
os.environ["TESTING"] = "true"

import pytest
from datetime import date, timedelta
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from main import app
from app.db.base import Base
from app.db.session import SessionLocal
from app.core.deps import get_db
from app.models.user import User, UserRole
from app.models.order import Order, OrderStatus, ItemCategory
from app.core.security import hash_password

TEST_DB_URL = "sqlite:///./test.db"

engine_test = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine_test)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="function", autouse=True)
def db():
    Base.metadata.create_all(bind=engine_test)
    db = TestingSessionLocal()
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine_test)


@pytest.fixture(scope="function")
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="function")
def alice(db):
    user = User(name="Alice", email="alice@test.com",
                hashed_password=hash_password("password123"), role=UserRole.CUSTOMER)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture(scope="function")
def bob(db):
    user = User(name="Bob", email="bob@test.com",
                hashed_password=hash_password("password123"), role=UserRole.CUSTOMER)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture(scope="function")
def staff_user(db):
    user = User(name="Staff", email="staff@test.com",
                hashed_password=hash_password("staffpass123"), role=UserRole.STAFF)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture(scope="function")
def alice_token(client, alice):
    resp = client.post("/auth/login", json={"email": "alice@test.com", "password": "password123"})
    return resp.json()["access_token"]


@pytest.fixture(scope="function")
def bob_token(client, bob):
    resp = client.post("/auth/login", json={"email": "bob@test.com", "password": "password123"})
    return resp.json()["access_token"]


@pytest.fixture(scope="function")
def staff_token(client, staff_user):
    resp = client.post("/auth/login", json={"email": "staff@test.com", "password": "staffpass123"})
    return resp.json()["access_token"]


@pytest.fixture(scope="function")
def alice_delivered_order(db, alice):
    """Alice has a delivered electronics order within return window."""
    order = Order(
        customer_id=alice.id,
        status=OrderStatus.DELIVERED,
        item_name="Test Phone",
        category=ItemCategory.ELECTRONICS,
        total_amount_paise=200000,  # ₹2000
        delivery_date=date.today() - timedelta(days=5),
    )
    db.add(order)
    db.commit()
    db.refresh(order)
    return order


@pytest.fixture(scope="function")
def alice_expired_order(db, alice):
    """Alice has a delivered electronics order with expired return window (>30 days ago)."""
    order = Order(
        customer_id=alice.id,
        status=OrderStatus.DELIVERED,
        item_name="Old Laptop",
        category=ItemCategory.ELECTRONICS,
        total_amount_paise=400000,  # ₹4000
        delivery_date=date.today() - timedelta(days=60),
    )
    db.add(order)
    db.commit()
    db.refresh(order)
    return order


@pytest.fixture(scope="function")
def alice_high_value_order(db, alice):
    """Alice has a delivered order with amount > ₹5000."""
    order = Order(
        customer_id=alice.id,
        status=OrderStatus.DELIVERED,
        item_name="Expensive Laptop",
        category=ItemCategory.ELECTRONICS,
        total_amount_paise=1000000,  # ₹10000
        delivery_date=date.today() - timedelta(days=3),
    )
    db.add(order)
    db.commit()
    db.refresh(order)
    return order


@pytest.fixture(scope="function")
def alice_ticket(client, alice_token, alice_delivered_order):
    resp = client.post(
        "/tickets",
        json={"subject": "Refund request", "description": "Need a refund",
              "category": "refund", "order_id": alice_delivered_order.id},
        headers={"Authorization": f"Bearer {alice_token}"},
    )
    assert resp.status_code == 201
    return resp.json()
