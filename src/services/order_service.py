from src.domain.order import Order, OrderItem, OrderStatus
from src.repositories.order_repository import OrderRepository
from src.services.order_queue import OrderQueue


class OrderNotFoundError(Exception):
    pass


class OrderService:
    def __init__(
        self,
        repository: OrderRepository,
        queue: OrderQueue,
    ):
        self.repository = repository
        self.queue = queue

    def create_order(
        self,
        customer_id: str,
        items: list[OrderItem],
        is_prime: bool = False,
        delivery_type: str = "standard",
    ) -> Order:
        order = Order(
            customer_id=customer_id,
            items=items,
            is_prime=is_prime,
            delivery_type=delivery_type,
        )

        self.repository.save(order)
        self.queue.push(order)

        return order

    def get_order(
        self,
        order_id: str,
    ) -> Order:
        order = self.repository.get_by_id(order_id)

        if order is None:
            raise OrderNotFoundError(
                f"Order {order_id} was not found."
            )

        return order

    def list_orders(self) -> list[Order]:
        return self.repository.list_all()

    def update_status(
        self,
        order_id: str,
        status: OrderStatus,
    ) -> Order:
        order = self.get_order(order_id)

        order.status = status

        self.repository.save(order)

        return order