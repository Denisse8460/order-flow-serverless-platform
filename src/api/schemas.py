from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

from src.domain.order import OrderStatus


class OrderItemCreate(BaseModel):
    product_id: str = Field(min_length=1)

    quantity: int = Field(
        gt=0
    )

    unit_price: float = Field(
        gt=0
    )


class OrderCreateRequest(BaseModel):
    customer_id: str = Field(
        min_length=1
    )

    items: list[OrderItemCreate] = Field(
        min_length=1
    )

    is_prime: bool = False

    delivery_type: Literal[
        "standard",
        "next_day",
        "same_day"
    ] = "standard"


class OrderStatusUpdate(BaseModel):
    status: OrderStatus


class OrderItemResponse(BaseModel):
    product_id: str
    quantity: int
    unit_price: float
    subtotal: float


class OrderResponse(BaseModel):
    order_id: str
    customer_id: str

    items: list[OrderItemResponse]

    is_prime: bool
    delivery_type: str

    status: OrderStatus

    created_at: datetime

    total: float
    priority_score: int