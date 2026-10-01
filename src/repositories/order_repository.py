from typing import Protocol

from src.domain.order import Order


class OrderRepository(Protocol):
    def save(self, order: Order) -> Order:
        ...

    def get_by_id(self, order_id: str) -> Order | None:
        ...

    def list_all(self) -> list[Order]:
        ...

    def claim_for_processing(
        self,
        order_id: str,
        lease_seconds: int = 300,
    ) -> bool:
        ...