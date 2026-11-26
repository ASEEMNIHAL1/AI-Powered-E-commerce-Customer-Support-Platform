"""Ticket service: CRUD with ownership enforcement."""
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.ticket import Ticket, TicketStatus
from app.models.order import Order
from app.models.user import User, UserRole
from app.schemas.ticket import TicketCreateRequest, TicketUpdateRequest
from app.services.audit_service import record_audit
from app.models.audit import AuditEventType


def create_ticket(db: Session, req: TicketCreateRequest, customer: User) -> Ticket:
    # If order_id provided, verify ownership
    if req.order_id is not None:
        order = db.query(Order).filter(Order.id == req.order_id).first()
        if not order or order.customer_id != customer.id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

    ticket = Ticket(
        customer_id=customer.id,
        order_id=req.order_id,
        subject=req.subject,
        description=req.description,
        category=req.category,
        priority=req.priority,
    )
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    record_audit(db, AuditEventType.TICKET_CREATED, actor_id=customer.id,
                 target_type="ticket", target_id=ticket.id)
    return ticket


def get_ticket_for_customer(db: Session, ticket_id: int, customer: User) -> Ticket:
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")
    if ticket.customer_id != customer.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")
    return ticket


def get_customer_tickets(db: Session, customer: User) -> list[Ticket]:
    return db.query(Ticket).filter(Ticket.customer_id == customer.id).order_by(Ticket.updated_at.desc()).all()


def update_ticket(db: Session, ticket_id: int, req: TicketUpdateRequest, actor: User) -> Ticket:
    # Staff can update any ticket; customers can only update their own
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")
    if actor.role == UserRole.CUSTOMER and ticket.customer_id != actor.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")

    old_status = ticket.status
    if req.status:
        ticket.status = req.status
    if req.priority:
        ticket.priority = req.priority
    db.commit()
    db.refresh(ticket)

    if req.status and req.status != old_status:
        record_audit(db, AuditEventType.TICKET_STATUS_CHANGED, actor_id=actor.id,
                     target_type="ticket", target_id=ticket.id,
                     detail=f"{old_status.value} -> {req.status.value}")
    return ticket
