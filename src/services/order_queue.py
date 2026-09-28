import heapq

from src.domain.order import Order
from src.services.priority_service import PriorityService

class OrderPriorityQueue:

    def __init__(self):
        self._queue = []

    def push(self, order: Order):
        priority = PriorityService.calculate_priority(order)

        heapq.heappush(
            self._queue,
            (-priority, order.created_at.timestamp(), order)
        )  # Use negative priority for max-heap behavior


    def pop(self) -> Order:
        if not self._queue:
            raise IndexError("The order queue is empty.")

        _, _, order = heapq.heappop(self._queue)

        return order
    def __len__(self):
        return len(self._queue)