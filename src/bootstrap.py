import boto3

from src.config import get_settings
from src.repositories.dynamodb_order_repository import (
    DynamoDBOrderRepository,
)
from src.repositories.in_memory_order_repository import (
    InMemoryOrderRepository,
)
from src.services.order_queue import OrderPriorityQueue
from src.services.order_service import OrderService


def create_order_service() -> OrderService:
    settings = get_settings()

    if settings.repository_backend == "memory":
        repository = InMemoryOrderRepository()

    elif settings.repository_backend == "dynamodb":
        dynamodb = boto3.resource(
            "dynamodb",
            region_name=settings.aws_region,
        )

        table = dynamodb.Table(
            settings.dynamodb_table_name
        )

        repository = DynamoDBOrderRepository(
            table=table
        )

    else:
        raise ValueError(
            "Unsupported repository backend: "
            f"{settings.repository_backend}"
        )

    queue = OrderPriorityQueue()

    return OrderService(
        repository=repository,
        queue=queue,
    )