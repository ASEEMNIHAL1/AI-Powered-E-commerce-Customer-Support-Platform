"""Pydantic schemas for orders."""
from datetime import date, datetime
from pydantic import BaseModel, ConfigDict

from app.models.order import OrderStatus, ItemCategory


class OrderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    customer_id: int
    status: OrderStatus
    item_name: str
    category: ItemCategory
    total_amount_paise: int
    delivery_date: date | None
    created_at: datetime

    @property
    def total_amount_rupees(self) -> float:
        return self.total_amount_paise / 100


class OrderListResponse(BaseModel):
    items: list[OrderResponse]
    total: int
