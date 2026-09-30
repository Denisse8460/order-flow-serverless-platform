from datetime import UTC, datetime, timedelta

from src.domain.order import Order, OrderStatus


class InMemoryOrderRepository:
    def __init__(self):
        self._orders: dict[str, Order] = {}
        self._processing_started_at: dict[str, datetime] = {}

    def save(self, order: Order) -> Order:
        self._orders[order.order_id] = order

        if order.status == OrderStatus.PROCESSING:
            self._processing_started_at.setdefault(
                order.order_id,
                datetime.now(UTC),
            )
        else:
            self._processing_started_at.pop(
                order.order_id,
                None,
            )

        return order

    def get_by_id(
        self,
        order_id: str,
    ) -> Order | None:
        return self._orders.get(order_id)

    def list_all(self) -> list[Order]:
        return list(self._orders.values())

    def claim_for_processing(
        self,
        order_id: str,
        lease_seconds: int = 300,
    ) -> bool:
        order = self.get_by_id(order_id)

        if order is None:
            return False

        if order.status == OrderStatus.COMPLETED:
            return False

        now = datetime.now(UTC)

        if order.status == OrderStatus.PROCESSING:
            processing_started_at = (
                self._processing_started_at.get(
                    order_id
                )
            )

            if processing_started_at is not None:
                lease_expiration = (
                    processing_started_at
                    + timedelta(
                        seconds=lease_seconds
                    )
                )

                if now < lease_expiration:
                    return False

        order.status = OrderStatus.PROCESSING

        self._orders[order_id] = order
        self._processing_started_at[order_id] = now

        return True