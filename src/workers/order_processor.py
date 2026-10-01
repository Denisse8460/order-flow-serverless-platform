from src.domain.order import Order, OrderStatus
from src.repositories.order_repository import (
    OrderRepository,
)


class OrderProcessingError(Exception):
    pass


class OrderProcessingInProgressError(
    OrderProcessingError
):
    pass


class OrderProcessor:
    def __init__(
        self,
        repository: OrderRepository,
    ):
        self.repository = repository

    def process(
        self,
        event: dict,
    ) -> Order:
        if event.get("event_type") != "OrderCreated":
            raise OrderProcessingError(
                "Unsupported event type."
            )

        order_id = event.get("order_id")

        if not order_id:
            raise OrderProcessingError(
                "The event does not contain an "
                "order_id."
            )

        order = self.repository.get_by_id(
            order_id
        )

        if order is None:
            raise OrderProcessingError(
                f"Order {order_id} was not found."
            )

        if order.status == OrderStatus.COMPLETED:
            return order

        claimed = (
            self.repository.claim_for_processing(
                order_id
            )
        )

        if not claimed:
            current_order = (
                self.repository.get_by_id(
                    order_id
                )
            )

            if current_order is None:
                raise OrderProcessingError(
                    f"Order {order_id} "
                    "was not found."
                )

            if (
                current_order.status
                == OrderStatus.COMPLETED
            ):
                return current_order

            raise OrderProcessingInProgressError(
                f"Order {order_id} is already "
                "being processed."
            )

        order = self.repository.get_by_id(
            order_id
        )

        if order is None:
            raise OrderProcessingError(
                f"Order {order_id} was not found."
            )

        try:
            # Real processing logic can be
            # introduced here later.

            order.status = OrderStatus.COMPLETED

            self.repository.save(order)

            return order

        except Exception:
            order.status = OrderStatus.PENDING
            self.repository.save(order)
            raise