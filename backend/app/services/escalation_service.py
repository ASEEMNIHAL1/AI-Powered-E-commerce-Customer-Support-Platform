"""Escalation service – staff review actions."""
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.escalation import Escalation, EscalationStatus
from app.models.refund import Refund, RefundStatus
from app.models.user import User
from app.models.audit import AuditEventType
from app.services.audit_service import record_audit


def get_all_escalations(db: Session) -> list[Escalation]:
    return db.query(Escalation).order_by(Escalation.created_at.desc()).all()


def decide_escalation(
    db: Session,
    escalation_id: int,
    decision: EscalationStatus,
    note: str | None,
    refund_decision: str | None,
    staff: User,
) -> Escalation:
    esc = db.query(Escalation).filter(Escalation.id == escalation_id).first()
    if not esc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Escalation not found")

    esc.status = decision
    esc.decision_note = note
    esc.assigned_to = staff.id

    # If a refund is linked and staff made a refund decision
    if esc.refund_id and refund_decision:
        refund = db.query(Refund).filter(Refund.id == esc.refund_id).first()
        if refund:
            if refund_decision == "approve":
                refund.status = RefundStatus.APPROVED
                refund.reviewed_by = staff.id
                refund.review_note = note
                record_audit(db, AuditEventType.REFUND_APPROVED, actor_id=staff.id,
                             target_type="refund", target_id=refund.id)
            elif refund_decision == "reject":
                refund.status = RefundStatus.REJECTED
                refund.reviewed_by = staff.id
                refund.review_note = note
                record_audit(db, AuditEventType.REFUND_REJECTED, actor_id=staff.id,
                             target_type="refund", target_id=refund.id)

    record_audit(db, AuditEventType.ESCALATION_DECISION, actor_id=staff.id,
                 target_type="escalation", target_id=esc.id,
                 detail=f"Decision: {decision.value}")
    db.commit()
    db.refresh(esc)
    return esc
