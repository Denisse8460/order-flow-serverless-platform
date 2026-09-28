from src.domain.order import Order

class PriorityService:

    @staticmethod
    def calculate_priority(order: Order) -> int:
        score = 0

        if order.is_prime:
            score += 40  # Prime customers get a higher priority

        if order.delivery_type == "same-day":
            score += 30  # Express delivery gets a higher priority
        elif order.delivery_type == "next-day":
            score += 20

        total = order.total()

        if total >= 1000:
            score += 20
        elif total >= 500:
            score += 10

        return score