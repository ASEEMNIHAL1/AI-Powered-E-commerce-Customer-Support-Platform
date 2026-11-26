"""Order service: fetch orders belonging to authenticated customer."""
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.order import Order
from app.models.user import User


def get_customer_orders(db: Session, customer: User) -> list[Order]:
    return db.query(Order).filter(Order.customer_id == customer.id).order_by(Order.created_at.desc()).all()


def get_order_for_customer(db: Session, order_id: int, customer: User) -> Order:
    """Fetch order and enforce ownership – prevents IDOR."""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    if order.customer_id != customer.id:
        # Return 404 to avoid leaking that the order exists for another user
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    return order
