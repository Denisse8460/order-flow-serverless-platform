from src.domain.order import Order, OrderItem
from src.services.order_queue import OrderPriorityQueue

def create_order(
        custumer_id,
        price,
        is_prime=False,
        delivery_type="standard"
):
    return Order(
        customer_id=custumer_id,
        items=[
            OrderItem(
                product_id="PRODUCT -001",
                quantity=1,
                unit_price=price
            )
        ],
        is_prime=is_prime,
        delivery_type=delivery_type
    )
def test_high_priority_order_is_processed_first():

    standard_order = create_order(
        custumer_id="CUSTOMER-001",
        price=200.0
    )

    primer_order =  create_order(
        custumer_id="CUSTOMER-002",
        price=500.0,
        is_prime=True,
        delivery_type="same-day"
    )

    queue = OrderPriorityQueue()

    queue.push(standard_order)
    queue.push(primer_order)

    next_order = queue.pop()
    assert next_order.customer_id == primer_order.customer_id