"""Order routes."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_active_customer
from app.models.user import User
from app.schemas.order import OrderResponse, OrderListResponse
from app.services.order_service import get_customer_orders, get_order_for_customer

router = APIRouter(prefix="/orders", tags=["orders"])


@router.get("", response_model=OrderListResponse)
def list_orders(db: Session = Depends(get_db), customer: User = Depends(get_current_active_customer)):
    orders = get_customer_orders(db, customer)
    return {"items": orders, "total": len(orders)}


@router.get("/{order_id}", response_model=OrderResponse)
def get_order(order_id: int, db: Session = Depends(get_db), customer: User = Depends(get_current_active_customer)):
    return get_order_for_customer(db, order_id, customer)
