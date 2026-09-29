import heapq
from itertools import count
from typing import Protocol

from src.domain.order import Order
from src.services.priority_service import PriorityService


class OrderQueue(Protocol):
    def push(self, order: Order) -> None:
        ...


class OrderPriorityQueue:
    def __init__(self):
        self._queue = []
        self._counter = count()

    def push(self, order: Order):
        priority = PriorityService.calculate_priority(
            order
        )

        heapq.heappush(
            self._queue,
            (
                -priority,
                order.created_at.timestamp(),
                next(self._counter),
                order,
            ),
        )

    def pop(self) -> Order:
        if not self._queue:
            raise IndexError(
                "The order queue is empty."
            )

        _, _, _, order = heapq.heappop(
            self._queue
        )

        return order

    def __len__(self):
        return len(self._queue)