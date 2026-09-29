from decimal import Decimal

from src.domain.order import Order, OrderItem
from src.repositories.dynamodb_order_repository import (
    DynamoDBOrderRepository,
)


class FakeDynamoDBTable:
    def __init__(self):
        self.items = {}

    def put_item(self, Item):
        self.items[Item["order_id"]] = Item

        return {
            "ResponseMetadata": {
                "HTTPStatusCode": 200,
            }
        }

    def get_item(self, Key):
        order_id = Key["order_id"]

        item = self.items.get(order_id)

        if item is None:
            return {}

        return {
            "Item": item,
        }

    def scan(self, **kwargs):
        return {
            "Items": list(
                self.items.values()
            )
        }


def create_sample_order():
    return Order(
        customer_id="CUSTOMER-001",
        items=[
            OrderItem(
                product_id="PRODUCT-001",
                quantity=2,
                unit_price=150.50,
            )
        ],
        is_prime=True,
        delivery_type="same_day",
    )


def test_save_order_to_dynamodb():
    table = FakeDynamoDBTable()

    repository = DynamoDBOrderRepository(
        table=table
    )

    order = create_sample_order()

    repository.save(order)

    stored_item = table.items[
        order.order_id
    ]

    assert stored_item["order_id"] == (
        order.order_id
    )

    assert stored_item["customer_id"] == (
        "CUSTOMER-001"
    )

    assert stored_item["status"] == "PENDING"

    assert stored_item["items"][0][
        "unit_price"
    ] == Decimal("150.50")


def test_get_order_from_dynamodb():
    table = FakeDynamoDBTable()

    repository = DynamoDBOrderRepository(
        table=table
    )

    original_order = create_sample_order()

    repository.save(original_order)

    saved_order = repository.get_by_id(
        original_order.order_id
    )

    assert saved_order is not None

    assert saved_order.order_id == (
        original_order.order_id
    )

    assert saved_order.customer_id == (
        "CUSTOMER-001"
    )

    assert saved_order.items[0].unit_price == (
        150.50
    )

    assert saved_order.is_prime is True

    assert saved_order.delivery_type == (
        "same_day"
    )


def test_get_unknown_order_returns_none():
    table = FakeDynamoDBTable()

    repository = DynamoDBOrderRepository(
        table=table
    )

    order = repository.get_by_id(
        "DOES-NOT-EXIST"
    )

    assert order is None


def test_list_orders_from_dynamodb():
    table = FakeDynamoDBTable()

    repository = DynamoDBOrderRepository(
        table=table
    )

    first_order = create_sample_order()

    second_order = Order(
        customer_id="CUSTOMER-002",
        items=[
            OrderItem(
                product_id="PRODUCT-002",
                quantity=1,
                unit_price=500.0,
            )
        ],
    )

    repository.save(first_order)
    repository.save(second_order)

    orders = repository.list_all()

    assert len(orders) == 2

    customer_ids = {
        order.customer_id
        for order in orders
    }

    assert customer_ids == {
        "CUSTOMER-001",
        "CUSTOMER-002",
    }