"""Ticket model."""
import enum
from datetime import datetime, timezone

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class TicketStatus(str, enum.Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    AWAITING_CUSTOMER = "awaiting_customer"
    ESCALATED = "escalated"
    RESOLVED = "resolved"
    CLOSED = "closed"


class TicketPriority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class TicketCategory(str, enum.Enum):
    REFUND = "refund"
    SHIPPING = "shipping"
    PRODUCT = "product"
    PAYMENT = "payment"
    ACCOUNT = "account"
    OTHER = "other"


class Ticket(Base):
    __tablename__ = "tickets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    customer_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    order_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("orders.id"), nullable=True, index=True)
    subject: Mapped[str] = mapped_column(String(300), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[TicketCategory] = mapped_column(Enum(TicketCategory), nullable=False)
    status: Mapped[TicketStatus] = mapped_column(Enum(TicketStatus), nullable=False, default=TicketStatus.OPEN)
    priority: Mapped[TicketPriority] = mapped_column(Enum(TicketPriority), nullable=False, default=TicketPriority.MEDIUM)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    # relationships
    customer: Mapped["User"] = relationship("User", back_populates="tickets")
    order: Mapped["Order | None"] = relationship("Order", back_populates="tickets")
    messages: Mapped[list["Message"]] = relationship("Message", back_populates="ticket", lazy="dynamic",
                                                      order_by="Message.created_at")
    refunds: Mapped[list["Refund"]] = relationship("Refund", back_populates="ticket", lazy="dynamic")
    escalations: Mapped[list["Escalation"]] = relationship("Escalation", back_populates="ticket", lazy="dynamic")
    notes: Mapped[list["Note"]] = relationship("Note", back_populates="ticket", lazy="dynamic")
