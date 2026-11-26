"""Refund routes."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_active_customer
from app.models.user import User
from app.schemas.refund import RefundCreateRequest, RefundResponse
from app.services.refund_service import process_refund, get_customer_refunds, get_refund_for_customer

router = APIRouter(prefix="/refunds", tags=["refunds"])


@router.post("", response_model=RefundResponse, status_code=201)
def create_refund(req: RefundCreateRequest, db: Session = Depends(get_db),
                  customer: User = Depends(get_current_active_customer)):
    result = process_refund(
        db=db,
        order_id=req.order_id,
        ticket_id=req.ticket_id,
        amount_paise=req.amount_paise,
        reason=req.reason,
        customer=customer,
    )
    return result["refund"]


@router.get("", response_model=list[RefundResponse])
def list_refunds(db: Session = Depends(get_db), customer: User = Depends(get_current_active_customer)):
    return get_customer_refunds(db, customer)


@router.get("/{refund_id}", response_model=RefundResponse)
def get_refund(refund_id: int, db: Session = Depends(get_db),
               customer: User = Depends(get_current_active_customer)):
    return get_refund_for_customer(db, refund_id, customer)
