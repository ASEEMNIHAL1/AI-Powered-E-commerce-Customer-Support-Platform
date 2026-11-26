"""Ticket routes."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_active_customer, get_current_user
from app.models.user import User
from app.schemas.ticket import TicketCreateRequest, TicketUpdateRequest, TicketResponse, TicketListResponse
from app.services.ticket_service import create_ticket, get_ticket_for_customer, get_customer_tickets, update_ticket

router = APIRouter(prefix="/tickets", tags=["tickets"])


@router.post("", response_model=TicketResponse, status_code=201)
def create(req: TicketCreateRequest, db: Session = Depends(get_db),
           customer: User = Depends(get_current_active_customer)):
    return create_ticket(db, req, customer)


@router.get("", response_model=TicketListResponse)
def list_tickets(db: Session = Depends(get_db), customer: User = Depends(get_current_active_customer)):
    tickets = get_customer_tickets(db, customer)
    return {"items": tickets, "total": len(tickets)}


@router.get("/{ticket_id}", response_model=TicketResponse)
def get_ticket(ticket_id: int, db: Session = Depends(get_db),
               customer: User = Depends(get_current_active_customer)):
    return get_ticket_for_customer(db, ticket_id, customer)


@router.patch("/{ticket_id}", response_model=TicketResponse)
def update(ticket_id: int, req: TicketUpdateRequest, db: Session = Depends(get_db),
           actor: User = Depends(get_current_user)):
    return update_ticket(db, ticket_id, req, actor)
