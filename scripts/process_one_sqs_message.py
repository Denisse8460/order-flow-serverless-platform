import json

import boto3

from src.config import get_settings
from src.repositories.dynamodb_order_repository import (
    DynamoDBOrderRepository,
)
from src.workers.order_processor import OrderProcessor


def main():
    settings = get_settings()

    if not settings.sqs_queue_url:
        raise ValueError(
            "ORDERFLOW_SQS_QUEUE_URL is required."
        )

    sqs = boto3.client(
        "sqs",
        region_name=settings.aws_region,
    )

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

    processor = OrderProcessor(
        repository=repository
    )

    response = sqs.receive_message(
        QueueUrl=settings.sqs_queue_url,
        MaxNumberOfMessages=1,
        WaitTimeSeconds=10,
        MessageAttributeNames=[
            "All",
        ],
        AttributeNames=[
            "ApproximateReceiveCount",
        ],
    )

    messages = response.get(
        "Messages",
        []
    )

    if not messages:
        print("No messages available.")
        return

    message = messages[0]

    event = json.loads(
        message["Body"]
    )

    print("Processing event:")
    print(event)

    try:
        order = processor.process(
            event
        )

        sqs.delete_message(
            QueueUrl=settings.sqs_queue_url,
            ReceiptHandle=message[
                "ReceiptHandle"
            ],
        )

        print(
            "Order completed:",
            order.order_id,
        )

        print(
            "SQS message deleted successfully."
        )

    except Exception:
        print(
            "Processing failed. "
            "The SQS message was NOT deleted."
        )

        raise


if __name__ == "__main__":
    main()