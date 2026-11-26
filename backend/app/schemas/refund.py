"""Pydantic schemas for refunds."""
from datetime import datetime
from pydantic import BaseModel, ConfigDict, field_validator

from app.models.refund import RefundStatus


class RefundCreateRequest(BaseModel):
    order_id: int
    ticket_id: int
    amount_paise: int
    reason: str

    @field_validator("amount_paise")
    @classmethod
    def amount_positive(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("Refund amount must be positive")
        return v

    @field_validator("reason")
    @classmethod
    def reason_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Reason must not be empty")
        return v.strip()


class RefundDecisionRequest(BaseModel):
    decision: RefundStatus  # APPROVED or REJECTED
    note: str | None = None


class RefundResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    order_id: int
    ticket_id: int
    amount_paise: int
    reason: str
    status: RefundStatus
    idempotency_key: str
    requested_by: int
    reviewed_by: int | None
    review_note: str | None
    created_at: datetime
    updated_at: datetime
