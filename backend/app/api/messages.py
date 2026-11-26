"""Message and AI chat routes."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_active_customer
from app.models.user import User
from app.schemas.message import MessageResponse, ChatRequest
from app.services.message_service import get_messages_for_ticket
from app.agents.support_agent import run_agent_turn

router = APIRouter(prefix="/tickets", tags=["messages"])


@router.get("/{ticket_id}/messages", response_model=list[MessageResponse])
def get_messages(ticket_id: int, db: Session = Depends(get_db),
                 customer: User = Depends(get_current_active_customer)):
    return get_messages_for_ticket(db, ticket_id, customer)


@router.post("/{ticket_id}/chat", response_model=MessageResponse)
def chat(ticket_id: int, req: ChatRequest, db: Session = Depends(get_db),
         customer: User = Depends(get_current_active_customer)):
    """
    Send a message to the AI agent and get a response.
    Both the customer message and agent response are persisted.
    """
    agent_reply = run_agent_turn(db, ticket_id, req.content, customer)
    # Return the last saved agent message
    from app.models.message import Message, SenderType
    msg = (
        db.query(Message)
        .filter(Message.ticket_id == ticket_id, Message.sender_type == SenderType.AGENT)
        .order_by(Message.created_at.desc())
        .first()
    )
    return msg
