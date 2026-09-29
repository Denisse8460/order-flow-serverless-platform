from src.domain.order import Order, OrderStatus
from src.repositories.order_repository import OrderRepository


class OrderProcessingError(Exception):
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
                "The event does not contain an order_id."
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

        order.status = OrderStatus.PROCESSING

        self.repository.save(order)

        # Later, the real business processing
        # will happen here.

        order.status = OrderStatus.COMPLETED

        self.repository.save(order)

        return order