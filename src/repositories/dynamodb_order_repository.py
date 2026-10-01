from datetime import UTC, datetime, timedelta
from decimal import Decimal

from botocore.exceptions import ClientError

from src.domain.order import Order, OrderItem, OrderStatus


class DynamoDBOrderRepository:
    def __init__(self, table):
        self.table = table

    def _order_to_item(
        self,
        order: Order,
    ) -> dict:
        return {
            "order_id": order.order_id,
            "customer_id": order.customer_id,
            "items": [
                {
                    "product_id": item.product_id,
                    "quantity": item.quantity,
                    "unit_price": Decimal(
                        str(item.unit_price)
                    ),
                }
                for item in order.items
            ],
            "is_prime": order.is_prime,
            "delivery_type": order.delivery_type,
            "status": order.status.value,
            "created_at": order.created_at.isoformat(),
        }

    def _item_to_order(
        self,
        item: dict,
    ) -> Order:
        return Order(
            order_id=item["order_id"],
            customer_id=item["customer_id"],
            items=[
                OrderItem(
                    product_id=order_item[
                        "product_id"
                    ],
                    quantity=int(
                        order_item["quantity"]
                    ),
                    unit_price=float(
                        order_item["unit_price"]
                    ),
                )
                for order_item in item["items"]
            ],
            is_prime=item["is_prime"],
            delivery_type=item["delivery_type"],
            status=OrderStatus(
                item["status"]
            ),
            created_at=datetime.fromisoformat(
                item["created_at"]
            ),
        )

    def save(
        self,
        order: Order,
    ) -> Order:
        self.table.put_item(
            Item=self._order_to_item(order)
        )

        return order

    def get_by_id(
        self,
        order_id: str,
    ) -> Order | None:
        response = self.table.get_item(
            Key={
                "order_id": order_id,
            }
        )

        item = response.get("Item")

        if item is None:
            return None

        return self._item_to_order(item)

    def list_all(self) -> list[Order]:
        items = []

        response = self.table.scan()

        items.extend(
            response.get(
                "Items",
                [],
            )
        )

        while "LastEvaluatedKey" in response:
            response = self.table.scan(
                ExclusiveStartKey=response[
                    "LastEvaluatedKey"
                ]
            )

            items.extend(
                response.get(
                    "Items",
                    [],
                )
            )

        return [
            self._item_to_order(item)
            for item in items
        ]

    def claim_for_processing(
        self,
        order_id: str,
        lease_seconds: int = 300,
    ) -> bool:
        now = datetime.now(UTC)

        stale_before = (
            now
            - timedelta(
                seconds=lease_seconds
            )
        )

        try:
            self.table.update_item(
                Key={
                    "order_id": order_id,
                },
                UpdateExpression=(
                    "SET #status = :processing, "
                    "processing_started_at = :now"
                ),
                ConditionExpression=(
                    "attribute_exists(order_id) "
                    "AND ("
                    "#status = :pending "
                    "OR #status = :failed "
                    "OR ("
                    "#status = :processing "
                    "AND ("
                    "attribute_not_exists("
                    "processing_started_at"
                    ") "
                    "OR processing_started_at "
                    "< :stale_before"
                    ")"
                    ")"
                    ")"
                ),
                ExpressionAttributeNames={
                    "#status": "status",
                },
                ExpressionAttributeValues={
                    ":pending": (
                        OrderStatus.PENDING.value
                    ),
                    ":processing": (
                        OrderStatus.PROCESSING.value
                    ),
                    ":failed": (
                        OrderStatus.FAILED.value
                    ),
                    ":now": int(
                        now.timestamp()
                    ),
                    ":stale_before": int(
                        stale_before.timestamp()
                    ),
                },
            )

            return True

        except ClientError as exc:
            error_code = exc.response[
                "Error"
            ]["Code"]

            if (
                error_code
                == "ConditionalCheckFailedException"
            ):
                return False

            raise