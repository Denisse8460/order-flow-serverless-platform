import json

from src.domain.order import Order
from src.services.priority_service import (
    PriorityService,
)


class SQSOrderQueue:
    def __init__(
        self,
        client,
        queue_url: str,
    ):
        self.client = client
        self.queue_url = queue_url

    def push(self, order: Order) -> None:
        priority_score = (
            PriorityService.calculate_priority(
                order
            )
        )

        message = {
            "event_type": "OrderCreated",
            "order_id": order.order_id,
            "customer_id": order.customer_id,
            "priority_score": priority_score,
            "created_at": (
                order.created_at.isoformat()
            ),
        }

        self.client.send_message(
            QueueUrl=self.queue_url,
            MessageBody=json.dumps(message),
            MessageAttributes={
                "priority_score": {
                    "DataType": "Number",
                    "StringValue": str(
                        priority_score
                    ),
                },
                "event_type": {
                    "DataType": "String",
                    "StringValue": (
                        "OrderCreated"
                    ),
                },
            },
        )