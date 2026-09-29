import json
import logging
import os

import boto3

from src.repositories.dynamodb_order_repository import (
    DynamoDBOrderRepository,
)
from src.workers.order_processor import OrderProcessor

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def build_processor() -> OrderProcessor:
    table_name = os.environ[
        "ORDERFLOW_DYNAMODB_TABLE"
    ]

    region = os.getenv(
        "AWS_REGION",
        "us-east-1",
    )

    dynamodb = boto3.resource(
        "dynamodb",
        region_name=region,
    )

    table = dynamodb.Table(
        table_name
    )

    repository = DynamoDBOrderRepository(
        table=table
    )

    return OrderProcessor(
        repository=repository
    )


def process_sqs_event(
    event: dict,
    processor: OrderProcessor,
) -> dict:
    failures = []

    for record in event.get(
        "Records",
        [],
    ):
        message_id = record.get(
            "messageId",
            "UNKNOWN",
        )

        try:
            body = json.loads(
                record["body"]
            )

            logger.info(
                "Processing SQS message %s "
                "for order %s",
                message_id,
                body.get("order_id"),
            )

            processor.process(
                body
            )

            logger.info(
                "Successfully processed "
                "SQS message %s",
                message_id,
            )

        except Exception:
            logger.exception(
                "Failed to process "
                "SQS message %s",
                message_id,
            )

            failures.append(
                {
                    "itemIdentifier": (
                        message_id
                    )
                }
            )

    return {
        "batchItemFailures": failures
    }


def lambda_handler(
    event,
    context,
):
    processor = build_processor()

    return process_sqs_event(
        event=event,
        processor=processor,
    )