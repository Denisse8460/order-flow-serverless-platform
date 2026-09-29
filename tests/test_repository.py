from src.domain.order import Order, OrderItem
from src.repositories.in_memory_order_repository import (
    InMemoryOrderRepository,
)


def test_repository_saves_and_retrieves_order():
    repository = InMemoryOrderRepository()

    order = Order(
        customer_id="CUSTOMER-001",
        items=[
            OrderItem(
                product_id="PRODUCT-001",
                quantity=1,
                unit_price=100.0,
            )
        ],
    )

    repository.save(order)

    saved_order = repository.get_by_id(
        order.order_id
    )

    assert saved_order is not None
    assert saved_order.order_id == order.order_id
    assert saved_order.customer_id == "CUSTOMER-001"