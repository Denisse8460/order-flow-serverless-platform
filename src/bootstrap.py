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
from src.services.sqs_order_queue import SQSOrderQueue


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

    if settings.queue_backend == "memory":
        queue = OrderPriorityQueue()

    elif settings.queue_backend == "sqs":
        if not settings.sqs_queue_url:
            raise ValueError(
                "ORDERFLOW_SQS_QUEUE_URL is required "
                "when ORDERFLOW_QUEUE=sqs"
            )

        sqs_client = boto3.client(
            "sqs",
            region_name=settings.aws_region,
        )

        queue = SQSOrderQueue(
            client=sqs_client,
            queue_url=settings.sqs_queue_url,
        )

    else:
        raise ValueError(
            "Unsupported queue backend: "
            f"{settings.queue_backend}"
        )

    return OrderService(
        repository=repository,
        queue=queue,
    )