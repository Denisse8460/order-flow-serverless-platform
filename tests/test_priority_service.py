from src.domain.order import Order, OrderItem
from src.services.priority_service import PriorityService


def create_order(
    price=100.0,
    is_prime=False,
    delivery_type="standard",
):
    return Order(
        customer_id="CUSTOMER-TEST",
        items=[
            OrderItem(
                product_id="PRODUCT-001",
                quantity=1,
                unit_price=price,
            )
        ],
        is_prime=is_prime,
        delivery_type=delivery_type,
    )


def test_standard_order_priority_is_zero():
    order = create_order()

    assert PriorityService.calculate_priority(order) == 0


def test_prime_customer_adds_40_points():
    order = create_order(
        is_prime=True
    )

    assert PriorityService.calculate_priority(order) == 40


def test_same_day_delivery_adds_30_points():
    order = create_order(
        delivery_type="same_day"
    )

    assert PriorityService.calculate_priority(order) == 30


def test_next_day_delivery_adds_20_points():
    order = create_order(
        delivery_type="next_day"
    )

    assert PriorityService.calculate_priority(order) == 20


def test_order_over_500_adds_10_points():
    order = create_order(
        price=500.0
    )

    assert PriorityService.calculate_priority(order) == 10


def test_order_over_1000_adds_20_points():
    order = create_order(
        price=1000.0
    )

    assert PriorityService.calculate_priority(order) == 20


def test_prime_same_day_order_scores_70():
    order = create_order(
        price=200.0,
        is_prime=True,
        delivery_type="same_day",
    )

    assert PriorityService.calculate_priority(order) == 70