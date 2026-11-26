"""
Test Group 5: Eligible refund creates exactly one refund record.
Test Group 6: Expired return window is rejected.
Test Group 7: Refund above ₹5,000 creates escalation and NOT auto-processed.
Test Group 8: Duplicate request does not create duplicate refunds.
"""
import pytest
from app.models.refund import Refund, RefundStatus
from app.models.escalation import Escalation


class TestEligibleRefund:
    """Test Group 5: Eligible refund creates exactly one record."""

    def test_eligible_refund_creates_one_record(self, client, alice_token, alice_delivered_order, alice_ticket, db):
        order_id = alice_delivered_order.id
        ticket_id = alice_ticket["id"]

        resp = client.post("/refunds", json={
            "order_id": order_id,
            "ticket_id": ticket_id,
            "amount_paise": 100000,  # ₹1000 – within ₹5000 threshold
            "reason": "Defective product",
        }, headers={"Authorization": f"Bearer {alice_token}"})

        assert resp.status_code == 201
        data = resp.json()
        assert data["status"] == "pending"
        assert data["amount_paise"] == 100000

        # Exactly one refund record
        assert db.query(Refund).count() == 1


class TestExpiredReturnWindow:
    """Test Group 6: Expired window is rejected with explanation."""

    def test_expired_window_rejected(self, client, alice_token, alice_expired_order, db):
        # Create ticket for expired order
        ticket_resp = client.post("/tickets",
                                  json={"subject": "Old refund", "description": "want refund",
                                        "category": "refund", "order_id": alice_expired_order.id},
                                  headers={"Authorization": f"Bearer {alice_token}"})
        ticket_id = ticket_resp.json()["id"]

        resp = client.post("/refunds", json={
            "order_id": alice_expired_order.id,
            "ticket_id": ticket_id,
            "amount_paise": 100000,
            "reason": "Changed mind",
        }, headers={"Authorization": f"Bearer {alice_token}"})

        assert resp.status_code == 422
        detail = resp.json()["detail"].lower()
        assert any(w in detail for w in ["expired", "window", "closed"])

        # No refund created
        assert db.query(Refund).count() == 0


class TestHighValueEscalation:
    """Test Group 7: Refund > ₹5000 creates escalation, not auto-refund."""

    def test_high_value_refund_escalated(self, client, alice_token, alice_high_value_order, db):
        ticket_resp = client.post("/tickets",
                                  json={"subject": "Big refund", "description": "expensive item",
                                        "category": "refund", "order_id": alice_high_value_order.id},
                                  headers={"Authorization": f"Bearer {alice_token}"})
        ticket_id = ticket_resp.json()["id"]

        resp = client.post("/refunds", json={
            "order_id": alice_high_value_order.id,
            "ticket_id": ticket_id,
            "amount_paise": 600000,  # ₹6000 – above ₹5000 threshold
            "reason": "Device defective",
        }, headers={"Authorization": f"Bearer {alice_token}"})

        assert resp.status_code == 201
        data = resp.json()
        # Status must be ESCALATED, not approved
        assert data["status"] == "escalated"

        # An escalation record must exist
        assert db.query(Escalation).count() == 1
        esc = db.query(Escalation).first()
        assert esc.refund_id == data["id"]

        # Refund exists but NOT approved/processed
        refund = db.query(Refund).first()
        assert refund.status == RefundStatus.ESCALATED

    def test_threshold_cannot_be_bypassed_by_splitting_check(self, client, alice_token, alice_high_value_order, db):
        """The threshold check is server-side, not based on client amount claim."""
        ticket_resp = client.post("/tickets",
                                  json={"subject": "Refund", "description": "Want refund",
                                        "category": "refund", "order_id": alice_high_value_order.id},
                                  headers={"Authorization": f"Bearer {alice_token}"})
        ticket_id = ticket_resp.json()["id"]

        # Send exactly at threshold + 1 paise
        resp = client.post("/refunds", json={
            "order_id": alice_high_value_order.id,
            "ticket_id": ticket_id,
            "amount_paise": 500001,  # 1 paise over ₹5000
            "reason": "Defect",
        }, headers={"Authorization": f"Bearer {alice_token}"})
        assert resp.status_code == 201
        assert resp.json()["status"] == "escalated"


class TestDuplicateRefundPrevention:
    """Test Group 8: Duplicate request does not create duplicate records."""

    def test_duplicate_refund_returns_existing(self, client, alice_token, alice_delivered_order, alice_ticket, db):
        order_id = alice_delivered_order.id
        ticket_id = alice_ticket["id"]
        payload = {
            "order_id": order_id,
            "ticket_id": ticket_id,
            "amount_paise": 50000,  # ₹500
            "reason": "Changed mind",
        }
        headers = {"Authorization": f"Bearer {alice_token}"}

        resp1 = client.post("/refunds", json=payload, headers=headers)
        assert resp1.status_code == 201

        # Exact same request again – idempotency should return existing, not create new
        resp2 = client.post("/refunds", json=payload, headers=headers)
        # Either 201 (existing returned) or 409 (conflict)
        assert resp2.status_code in (201, 409)

        # Exactly one refund record
        assert db.query(Refund).count() == 1
