import pytest

from src.domain.order import Order, OrderItem, OrderStatus
from src.repositories.in_memory_order_repository import (
    InMemoryOrderRepository,
)
from src.workers.order_processor import (
    OrderProcessingError,
    OrderProcessor,
)


def create_order(
    repository: InMemoryOrderRepository,
) -> Order:
    order = Order(
        customer_id="CUSTOMER-001",
        items=[
            OrderItem(
                product_id="PRODUCT-001",
                quantity=1,
                unit_price=200.0,
            )
        ],
    )

    repository.save(order)

    return order


def test_process_order_marks_it_completed():
    repository = InMemoryOrderRepository()

    order = create_order(repository)

    processor = OrderProcessor(
        repository=repository
    )

    result = processor.process(
        {
            "event_type": "OrderCreated",
            "order_id": order.order_id,
        }
    )

    assert result.status == OrderStatus.COMPLETED

    stored_order = repository.get_by_id(
        order.order_id
    )

    assert stored_order is not None
    assert stored_order.status == OrderStatus.COMPLETED


def test_completed_order_is_idempotent():
    repository = InMemoryOrderRepository()

    order = create_order(repository)

    order.status = OrderStatus.COMPLETED
    repository.save(order)

    processor = OrderProcessor(
        repository=repository
    )

    result = processor.process(
        {
            "event_type": "OrderCreated",
            "order_id": order.order_id,
        }
    )

    assert result.status == OrderStatus.COMPLETED


def test_unknown_order_raises_error():
    repository = InMemoryOrderRepository()

    processor = OrderProcessor(
        repository=repository
    )

    with pytest.raises(
        OrderProcessingError
    ):
        processor.process(
            {
                "event_type": "OrderCreated",
                "order_id": "DOES-NOT-EXIST",
            }
        )


def test_invalid_event_type_raises_error():
    repository = InMemoryOrderRepository()

    order = create_order(repository)

    processor = OrderProcessor(
        repository=repository
    )

    with pytest.raises(
        OrderProcessingError
    ):
        processor.process(
            {
                "event_type": "SomethingElse",
                "order_id": order.order_id,
            }
        )