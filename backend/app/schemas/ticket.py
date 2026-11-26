"""Pydantic schemas for tickets."""
from datetime import datetime
from pydantic import BaseModel, ConfigDict, field_validator

from app.models.ticket import TicketStatus, TicketPriority, TicketCategory


class TicketCreateRequest(BaseModel):
    subject: str
    description: str
    category: TicketCategory
    order_id: int | None = None
    priority: TicketPriority = TicketPriority.MEDIUM

    @field_validator("subject")
    @classmethod
    def subject_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Subject must not be empty")
        return v.strip()


class TicketUpdateRequest(BaseModel):
    status: TicketStatus | None = None
    priority: TicketPriority | None = None


class TicketResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    customer_id: int
    order_id: int | None
    subject: str
    description: str
    category: TicketCategory
    status: TicketStatus
    priority: TicketPriority
    created_at: datetime
    updated_at: datetime


class TicketListResponse(BaseModel):
    items: list[TicketResponse]
    total: int
