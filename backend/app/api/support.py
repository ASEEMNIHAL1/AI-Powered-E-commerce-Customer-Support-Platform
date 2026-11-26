"""Support staff routes: ticket list, escalations, notes, refund decisions."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_staff
from app.models.user import User
from app.models.ticket import Ticket
from app.schemas.ticket import TicketResponse, TicketListResponse, TicketUpdateRequest
from app.schemas.escalation import EscalationResponse, EscalationDecisionRequest, NoteCreateRequest, NoteResponse
from app.services.escalation_service import get_all_escalations, decide_escalation
from app.services.ticket_service import update_ticket
from app.models.escalation import Note

router = APIRouter(prefix="/support", tags=["support"])


@router.get("/tickets", response_model=TicketListResponse)
def list_all_tickets(
    status: str | None = None,
    priority: str | None = None,
    db: Session = Depends(get_db),
    staff: User = Depends(get_current_staff),
):
    q = db.query(Ticket)
    if status:
        q = q.filter(Ticket.status == status)
    if priority:
        q = q.filter(Ticket.priority == priority)
    tickets = q.order_by(Ticket.updated_at.desc()).all()
    return {"items": tickets, "total": len(tickets)}


@router.get("/tickets/{ticket_id}", response_model=TicketResponse)
def get_ticket_detail(ticket_id: int, db: Session = Depends(get_db), staff: User = Depends(get_current_staff)):
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        from fastapi import HTTPException, status
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")
    return ticket


@router.patch("/tickets/{ticket_id}", response_model=TicketResponse)
def update_ticket_status(ticket_id: int, req: TicketUpdateRequest, db: Session = Depends(get_db),
                         staff: User = Depends(get_current_staff)):
    return update_ticket(db, ticket_id, req, staff)


@router.get("/escalations", response_model=list[EscalationResponse])
def list_escalations(db: Session = Depends(get_db), staff: User = Depends(get_current_staff)):
    return get_all_escalations(db)


@router.post("/escalations/{escalation_id}/decision", response_model=EscalationResponse)
def make_decision(
    escalation_id: int,
    req: EscalationDecisionRequest,
    db: Session = Depends(get_db),
    staff: User = Depends(get_current_staff),
):
    return decide_escalation(db, escalation_id, req.decision, req.note, req.refund_decision, staff)


@router.post("/tickets/{ticket_id}/notes", response_model=NoteResponse, status_code=201)
def add_note(ticket_id: int, req: NoteCreateRequest, db: Session = Depends(get_db),
             staff: User = Depends(get_current_staff)):
    note = Note(ticket_id=ticket_id, author_id=staff.id, content=req.content)
    db.add(note)
    db.commit()
    db.refresh(note)
    return note


@router.get("/tickets/{ticket_id}/notes", response_model=list[NoteResponse])
def get_notes(ticket_id: int, db: Session = Depends(get_db), staff: User = Depends(get_current_staff)):
    return db.query(Note).filter(Note.ticket_id == ticket_id).order_by(Note.created_at.desc()).all()
