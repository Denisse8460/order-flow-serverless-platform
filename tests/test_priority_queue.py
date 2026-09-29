from src.domain.order import Order, OrderItem
from src.services.order_queue import OrderPriorityQueue


def create_order(
    customer_id,
    price,
    is_prime=False,
    delivery_type="standard"
):
    return Order(
        customer_id=customer_id,
        items=[
            OrderItem(
                product_id="PRODUCT-001",
                quantity=1,
                unit_price=price
            )
        ],
        is_prime=is_prime,
        delivery_type=delivery_type
    )


def test_high_priority_order_is_processed_first():

    standard_order = create_order(
        customer_id="CUSTOMER-001",
        price=200.0
    )

    prime_order = create_order(
        customer_id="CUSTOMER-002",
        price=500.0,
        is_prime=True,
        delivery_type="same_day"
    )

    queue = OrderPriorityQueue()

    queue.push(standard_order)
    queue.push(prime_order)

    next_order = queue.pop()

    assert next_order.customer_id == prime_order.customer_id