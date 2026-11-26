"""Pydantic schemas for escalations and notes."""
from datetime import datetime
from pydantic import BaseModel, ConfigDict

from app.models.escalation import EscalationPriority, EscalationStatus


class EscalationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    ticket_id: int
    refund_id: int | None
    summary: str
    priority: EscalationPriority
    status: EscalationStatus
    assigned_to: int | None
    decision_note: str | None
    created_at: datetime
    updated_at: datetime


class EscalationDecisionRequest(BaseModel):
    decision: EscalationStatus
    note: str | None = None
    refund_decision: str | None = None  # "approve" | "reject"


class NoteCreateRequest(BaseModel):
    content: str


class NoteResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    ticket_id: int
    author_id: int
    content: str
    created_at: datetime
