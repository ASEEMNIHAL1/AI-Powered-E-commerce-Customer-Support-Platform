"""Audit service helper."""
from sqlalchemy.orm import Session
from app.models.audit import AuditLog, AuditEventType


def record_audit(
    db: Session,
    event_type: AuditEventType,
    actor_id: int | None = None,
    target_type: str | None = None,
    target_id: int | None = None,
    detail: str | None = None,
) -> None:
    log = AuditLog(
        event_type=event_type,
        actor_id=actor_id,
        target_type=target_type,
        target_id=target_id,
        detail=detail,
    )
    db.add(log)
    db.commit()
