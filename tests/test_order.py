from src.domain.order import Order, OrderItem, OrderStatus


def test_order_total():
    items = [
        OrderItem(
            product_id="P001",
            quantity=2,
            unit_price=100.0
        ),
        OrderItem(
            product_id="P002",
            quantity=1,
            unit_price=50.0
        )
    ]

    order = Order(
        customer_id="C001",
        items=items
    )

    assert order.total() == 250.0


def test_new_order_status_is_pending():
    order = Order(
        customer_id="C001",
        items=[]
    )

    assert order.status == OrderStatus.PENDING