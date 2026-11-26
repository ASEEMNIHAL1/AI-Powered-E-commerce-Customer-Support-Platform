"""
Test Group 3: Ticket and messages persist and can be retrieved by owner.
Test Group 4: Missing order ID causes agent to ask for clarification (no refund executed).
"""
import pytest
from unittest.mock import patch


class TestTicketAndMessagePersistence:
    """Test Group 3: Messages are saved and retrievable."""

    def test_create_ticket_persists(self, client, alice_token):
        resp = client.post("/tickets",
                           json={"subject": "Need help", "description": "Details here", "category": "other"},
                           headers={"Authorization": f"Bearer {alice_token}"})
        assert resp.status_code == 201
        ticket_id = resp.json()["id"]

        # Retrieve it
        resp2 = client.get(f"/tickets/{ticket_id}", headers={"Authorization": f"Bearer {alice_token}"})
        assert resp2.status_code == 200
        assert resp2.json()["subject"] == "Need help"

    def test_messages_persist_and_load(self, client, alice_token, alice_ticket):
        ticket_id = alice_ticket["id"]

        # Send a chat message – agent will respond (mock mode)
        client.post(f"/tickets/{ticket_id}/chat",
                    json={"content": "Hello, I need help"},
                    headers={"Authorization": f"Bearer {alice_token}"})

        # Retrieve messages
        resp = client.get(f"/tickets/{ticket_id}/messages",
                          headers={"Authorization": f"Bearer {alice_token}"})
        assert resp.status_code == 200
        messages = resp.json()
        assert len(messages) >= 2  # customer + agent
        sender_types = {m["sender_type"] for m in messages}
        assert "customer" in sender_types
        assert "agent" in sender_types

    def test_ticket_list_shows_own_tickets(self, client, alice_token, alice_ticket):
        resp = client.get("/tickets", headers={"Authorization": f"Bearer {alice_token}"})
        assert resp.status_code == 200
        ids = [t["id"] for t in resp.json()["items"]]
        assert alice_ticket["id"] in ids


class TestMissingOrderIdClarification:
    """Test Group 4: If order ID missing, agent asks for it. No refund executed."""

    def test_refund_without_order_id_triggers_clarification(self, client, alice_token, db):
        from app.models.refund import Refund

        # Create ticket WITHOUT order_id
        ticket_resp = client.post("/tickets",
                                  json={"subject": "Refund", "description": "I want refund", "category": "refund"},
                                  headers={"Authorization": f"Bearer {alice_token}"})
        ticket_id = ticket_resp.json()["id"]

        # Send vague refund message
        chat_resp = client.post(f"/tickets/{ticket_id}/chat",
                                json={"content": "I want a refund please"},
                                headers={"Authorization": f"Bearer {alice_token}"})
        assert chat_resp.status_code == 200
        agent_reply = chat_resp.json()["content"].lower()

        # Agent should ask for order ID, not process refund
        assert any(w in agent_reply for w in ["order", "id", "provide", "share", "number"])

        # No refund should have been created
        assert db.query(Refund).count() == 0
