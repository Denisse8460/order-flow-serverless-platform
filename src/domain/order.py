from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List
import uuid


class OrderStatus(str, Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


@dataclass
class OrderItem:
    product_id: str
    quantity: int
    unit_price: float

    def subtotal(self) -> float:
        return self.quantity * self.unit_price


@dataclass
class Order:
    customer_id: str
    items: List[OrderItem]

    is_prime: bool = False
    delivery_type: str = "standard"

    order_id: str = field(
        default_factory=lambda: str(uuid.uuid4())
    )

    status: OrderStatus = OrderStatus.PENDING

    created_at: datetime = field(
        default_factory=datetime.utcnow
    )

    def total(self) -> float:
        return sum(item.subtotal() for item in self.items)