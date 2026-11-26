"""Message service – chat persistence."""
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.message import Message, SenderType
from app.models.ticket import Ticket
from app.models.user import User


def get_messages_for_ticket(db: Session, ticket_id: int, customer: User) -> list[Message]:
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket or ticket.customer_id != customer.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")
    return db.query(Message).filter(Message.ticket_id == ticket_id).order_by(Message.created_at.asc()).all()


def save_message(
    db: Session,
    ticket_id: int,
    sender_type: SenderType,
    content: str,
    sender_id: int | None = None,
) -> Message:
    msg = Message(
        ticket_id=ticket_id,
        sender_type=sender_type,
        content=content,
        sender_id=sender_id,
    )
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return msg
