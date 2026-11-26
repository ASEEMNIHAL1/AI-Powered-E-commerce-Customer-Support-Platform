"""Audit log model for sensitive operations."""
import enum
from datetime import datetime, timezone

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class AuditEventType(str, enum.Enum):
    REFUND_REQUESTED = "refund_requested"
    REFUND_APPROVED = "refund_approved"
    REFUND_REJECTED = "refund_rejected"
    REFUND_ESCALATED = "refund_escalated"
    ESCALATION_CREATED = "escalation_created"
    ESCALATION_DECISION = "escalation_decision"
    TICKET_CREATED = "ticket_created"
    TICKET_STATUS_CHANGED = "ticket_status_changed"
    LOGIN = "login"
    UNAUTHORIZED_ACCESS = "unauthorized_access"


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    event_type: Mapped[AuditEventType] = mapped_column(Enum(AuditEventType), nullable=False, index=True)
    actor_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    target_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    target_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    detail: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )
