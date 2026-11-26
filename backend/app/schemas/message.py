"""Pydantic schemas for messages."""
from datetime import datetime
from pydantic import BaseModel, ConfigDict, field_validator

from app.models.message import SenderType


class MessageCreateRequest(BaseModel):
    content: str

    @field_validator("content")
    @classmethod
    def content_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Message content must not be empty")
        return v.strip()


class ChatRequest(BaseModel):
    content: str

    @field_validator("content")
    @classmethod
    def content_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Message must not be empty")
        return v.strip()


class MessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    ticket_id: int
    sender_type: SenderType
    sender_id: int | None
    content: str
    created_at: datetime
