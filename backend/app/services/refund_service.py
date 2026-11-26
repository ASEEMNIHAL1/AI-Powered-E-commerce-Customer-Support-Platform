"""
Refund service – all business rules live here, NOT in the AI agent.

Business rules enforced:
1. Customer must own the order
2. Order must be delivered
3. Return window must not have expired
4. Requested amount must not exceed order amount
5. No existing approved/pending refund on the same order (idempotency)
6. Amounts > ₹5000 (500000 paise) escalate automatically; never auto-processed
7. Idempotency key prevents duplicate records
"""
import hashlib
from datetime import date, datetime, timezone, timedelta
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status

from app.core.config import settings
from app.models.order import Order, OrderStatus, ItemCategory
from app.models.refund import Refund, RefundStatus
from app.models.ticket import Ticket
from app.models.escalation import Escalation, EscalationPriority, EscalationStatus
from app.models.audit import AuditEventType
from app.services.audit_service import record_audit
from app.models.user import User

# Return window in days per category
RETURN_WINDOW_DAYS: dict[ItemCategory, int] = {
    ItemCategory.ELECTRONICS: 30,
    ItemCategory.CLOTHING: 15,
    ItemCategory.FOOD: 7,
    ItemCategory.BOOKS: 15,
    ItemCategory.HOME: 15,
    ItemCategory.OTHER: 15,
}


def _compute_idempotency_key(order_id: int, customer_id: int, amount_paise: int) -> str:
    raw = f"{order_id}:{customer_id}:{amount_paise}"
    return hashlib.sha256(raw.encode()).hexdigest()


def _check_return_window(order: Order) -> tuple[bool, str]:
    if not order.delivery_date:
        return False, "Order has no delivery date recorded"
    if order.status != OrderStatus.DELIVERED:
        return False, f"Order is not in delivered state (current: {order.status.value})"

    window_days = RETURN_WINDOW_DAYS.get(order.category, 15)
    cutoff = order.delivery_date + timedelta(days=window_days)
    today = date.today()
    if today > cutoff:
        return False, (
            f"Return window of {window_days} days for {order.category.value} has expired. "
            f"Delivery was on {order.delivery_date}, window closed on {cutoff}."
        )
    return True, ""


def process_refund(
    db: Session,
    order_id: int,
    ticket_id: int,
    amount_paise: int,
    reason: str,
    customer: User,
) -> dict:
    """
    Validate and process a refund request.
    Returns {"refund": Refund, "escalated": bool, "message": str}
    """
    # --- 1. Ownership check ---
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order or order.customer_id != customer.id:
        record_audit(db, AuditEventType.UNAUTHORIZED_ACCESS, actor_id=customer.id,
                     detail=f"Attempted refund on order {order_id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

    # --- 2. Ticket ownership check ---
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket or ticket.customer_id != customer.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")

    # --- 3. Amount validation ---
    if amount_paise <= 0:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Refund amount must be positive")
    if amount_paise > order.total_amount_paise:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Requested refund (₹{amount_paise/100:.2f}) exceeds order total (₹{order.total_amount_paise/100:.2f})"
        )

    # --- 4. Return window check ---
    eligible, reason_msg = _check_return_window(order)
    if not eligible:
        record_audit(db, AuditEventType.REFUND_REJECTED, actor_id=customer.id,
                     target_type="order", target_id=order_id, detail=reason_msg)
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=reason_msg)

    # --- 5. Idempotency check ---
    idem_key = _compute_idempotency_key(order_id, customer.id, amount_paise)
    existing = db.query(Refund).filter(Refund.idempotency_key == idem_key).first()
    if existing:
        return {"refund": existing, "escalated": existing.status == RefundStatus.ESCALATED, "message": "Duplicate request – returning existing record"}

    # --- 6. Duplicate active refund check ---
    active = db.query(Refund).filter(
        Refund.order_id == order_id,
        Refund.status.in_([RefundStatus.PENDING, RefundStatus.APPROVED, RefundStatus.ESCALATED])
    ).first()
    if active:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"A refund for this order already exists with status: {active.status.value}"
        )

    # --- 7. ₹5000 threshold – HARD enforcement on backend ---
    # This is never read from the frontend or from LLM output
    escalation_threshold = settings.refund_escalation_threshold  # 500000 paise
    needs_escalation = amount_paise > escalation_threshold

    refund = Refund(
        order_id=order_id,
        ticket_id=ticket_id,
        amount_paise=amount_paise,
        reason=reason,
        status=RefundStatus.ESCALATED if needs_escalation else RefundStatus.PENDING,
        idempotency_key=idem_key,
        requested_by=customer.id,
    )
    db.add(refund)
    db.flush()  # get refund.id before creating escalation

    escalation = None
    if needs_escalation:
        escalation = Escalation(
            ticket_id=ticket_id,
            refund_id=refund.id,
            summary=(
                f"Refund of ₹{amount_paise/100:.2f} for order #{order_id} requires human review. "
                f"Reason: {reason}"
            ),
            priority=EscalationPriority.HIGH,
            status=EscalationStatus.OPEN,
        )
        db.add(escalation)
        record_audit(db, AuditEventType.REFUND_ESCALATED, actor_id=customer.id,
                     target_type="refund", target_id=refund.id,
                     detail=f"Amount ₹{amount_paise/100:.2f} exceeds threshold ₹{escalation_threshold/100:.2f}")
    else:
        record_audit(db, AuditEventType.REFUND_REQUESTED, actor_id=customer.id,
                     target_type="refund", target_id=refund.id,
                     detail=f"Amount ₹{amount_paise/100:.2f}")

    db.commit()
    db.refresh(refund)

    msg = (
        f"Refund of ₹{amount_paise/100:.2f} escalated for human review (exceeds ₹{escalation_threshold/100:.2f})"
        if needs_escalation
        else f"Refund of ₹{amount_paise/100:.2f} created with status: pending"
    )
    return {"refund": refund, "escalated": needs_escalation, "message": msg}


def get_customer_refunds(db: Session, customer: User) -> list[Refund]:
    return (
        db.query(Refund)
        .join(Order, Refund.order_id == Order.id)
        .filter(Order.customer_id == customer.id)
        .order_by(Refund.created_at.desc())
        .all()
    )


def get_refund_for_customer(db: Session, refund_id: int, customer: User) -> Refund:
    refund = db.query(Refund).filter(Refund.id == refund_id).first()
    if not refund:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Refund not found")
    order = db.query(Order).filter(Order.id == refund.order_id).first()
    if not order or order.customer_id != customer.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Refund not found")
    return refund
