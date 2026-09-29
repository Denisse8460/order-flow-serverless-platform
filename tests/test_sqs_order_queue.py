import json

from src.domain.order import Order, OrderItem
from src.services.sqs_order_queue import (
    SQSOrderQueue,
)


class FakeSQSClient:
    def __init__(self):
        self.messages = []

    def send_message(self, **kwargs):
        self.messages.append(kwargs)

        return {
            "MessageId": "TEST-MESSAGE-ID"
        }


def create_sample_order():
    return Order(
        customer_id="CUSTOMER-001",
        items=[
            OrderItem(
                product_id="PRODUCT-001",
                quantity=1,
                unit_price=200.0,
            )
        ],
        is_prime=True,
        delivery_type="same_day",
    )


def test_push_sends_order_to_sqs():
    client = FakeSQSClient()

    queue = SQSOrderQueue(
        client=client,
        queue_url="https://example.com/test",
    )

    order = create_sample_order()

    queue.push(order)

    assert len(client.messages) == 1

    sent_message = client.messages[0]

    body = json.loads(
        sent_message["MessageBody"]
    )

    assert body["event_type"] == (
        "OrderCreated"
    )

    assert body["order_id"] == (
        order.order_id
    )

    assert body["customer_id"] == (
        "CUSTOMER-001"
    )

    assert body["priority_score"] == 70


def test_priority_score_is_sent_as_attribute():
    client = FakeSQSClient()

    queue = SQSOrderQueue(
        client=client,
        queue_url="https://example.com/test",
    )

    order = create_sample_order()

    queue.push(order)

    attributes = client.messages[0][
        "MessageAttributes"
    ]

    assert attributes[
        "priority_score"
    ]["StringValue"] == "70"

    assert attributes[
        "event_type"
    ]["StringValue"] == "OrderCreated"