"""
Test Group 1: Unauthenticated access is blocked.
Test Group 2: Customer A cannot access Customer B's order or ticket.
"""
import pytest


class TestUnauthenticatedBlocked:
    """Test Group 1: All protected endpoints return 401 without token."""

    def test_orders_blocked(self, client):
        assert client.get("/orders").status_code == 401

    def test_order_detail_blocked(self, client):
        assert client.get("/orders/1").status_code == 401

    def test_tickets_blocked(self, client):
        assert client.get("/tickets").status_code == 401

    def test_create_ticket_blocked(self, client):
        resp = client.post("/tickets", json={"subject": "x", "description": "y", "category": "other"})
        assert resp.status_code == 401

    def test_chat_blocked(self, client):
        assert client.post("/tickets/1/chat", json={"content": "hi"}).status_code == 401

    def test_refunds_blocked(self, client):
        assert client.get("/refunds").status_code == 401

    def test_support_tickets_blocked(self, client):
        assert client.get("/support/tickets").status_code == 401

    def test_support_escalations_blocked(self, client):
        assert client.get("/support/escalations").status_code == 401

    def test_me_blocked(self, client):
        assert client.get("/auth/me").status_code == 401


class TestIsolationBetweenCustomers:
    """Test Group 2: Customer A cannot access Customer B's resources."""

    def test_cannot_access_other_order(self, client, alice_token, bob, db):
        from app.models.order import Order, OrderStatus, ItemCategory
        from datetime import date
        bob_order = Order(customer_id=bob.id, status=OrderStatus.DELIVERED, item_name="Bob's item",
                          category=ItemCategory.ELECTRONICS, total_amount_paise=100000,
                          delivery_date=date.today())
        db.add(bob_order)
        db.commit()
        resp = client.get(f"/orders/{bob_order.id}", headers={"Authorization": f"Bearer {alice_token}"})
        assert resp.status_code == 404  # returns 404, not exposing Bob's data

    def test_cannot_access_other_ticket(self, client, alice_token, bob, bob_token, db):
        from app.models.order import Order, OrderStatus, ItemCategory
        from datetime import date
        bob_order = Order(customer_id=bob.id, status=OrderStatus.DELIVERED, item_name="Bob's item",
                          category=ItemCategory.ELECTRONICS, total_amount_paise=100000,
                          delivery_date=date.today())
        db.add(bob_order)
        db.commit()

        # Bob creates a ticket
        resp = client.post("/tickets",
                           json={"subject": "Bob's ticket", "description": "Bob's issue", "category": "other"},
                           headers={"Authorization": f"Bearer {bob_token}"})
        assert resp.status_code == 201
        bob_ticket_id = resp.json()["id"]

        # Alice tries to read Bob's ticket
        resp = client.get(f"/tickets/{bob_ticket_id}", headers={"Authorization": f"Bearer {alice_token}"})
        assert resp.status_code == 404

    def test_customer_cannot_access_support_routes(self, client, alice_token):
        resp = client.get("/support/tickets", headers={"Authorization": f"Bearer {alice_token}"})
        assert resp.status_code == 403
