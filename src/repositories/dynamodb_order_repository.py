from datetime import datetime
from decimal import Decimal

from src.domain.order import Order, OrderItem, OrderStatus


class DynamoDBOrderRepository:
    def __init__(self, table):
        self.table = table

    def _order_to_item(self, order: Order) -> dict:
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

    def _item_to_order(self, item: dict) -> Order:
        return Order(
            order_id=item["order_id"],
            customer_id=item["customer_id"],
            items=[
                OrderItem(
                    product_id=order_item["product_id"],
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
            status=OrderStatus(item["status"]),
            created_at=datetime.fromisoformat(
                item["created_at"]
            ),
        )

    def save(self, order: Order) -> Order:
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
            response.get("Items", [])
        )

        while "LastEvaluatedKey" in response:
            response = self.table.scan(
                ExclusiveStartKey=response[
                    "LastEvaluatedKey"
                ]
            )

            items.extend(
                response.get("Items", [])
            )

        return [
            self._item_to_order(item)
            for item in items
        ]