import json
import logging
import os

import boto3

from src.observability.logging import log_event
from src.repositories.dynamodb_order_repository import DynamoDBOrderRepository
from src.workers.order_processor import OrderProcessor

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def build_processor() -> OrderProcessor:
    table_name = os.environ["ORDERFLOW_DYNAMODB_TABLE"]
    region = os.getenv("AWS_REGION", "us-east-1")

    dynamodb = boto3.resource(
        "dynamodb",
        region_name=region,
    )

    table = dynamodb.Table(table_name)

    repository = DynamoDBOrderRepository(
        table=table,
    )

    return OrderProcessor(
        repository=repository,
    )


def process_sqs_event(
    event: dict,
    processor: OrderProcessor,
) -> dict:
    failures = []

    for record in event.get("Records", []):
        message_id = record.get(
            "messageId",
            "UNKNOWN",
        )

        order_id = None
        event_type = None

        try:
            body = json.loads(record["body"])

            order_id = body.get("order_id")
            event_type = body.get("event_type")

            log_event(
                logger,
                logging.INFO,
                "order_processing_started",
                message_id=message_id,
                order_id=order_id,
                event_type=event_type,
            )

            processor.process(body)

            log_event(
                logger,
                logging.INFO,
                "order_processing_completed",
                message_id=message_id,
                order_id=order_id,
                event_type=event_type,
            )

        except Exception as exc:
            log_event(
                logger,
                logging.ERROR,
                "order_processing_failed",
                message_id=message_id,
                order_id=order_id,
                event_type=event_type,
                error_type=type(exc).__name__,
                error_message=str(exc),
            )

            logger.exception(
                "Order processing failed for message %s",
                message_id,
            )

            failures.append(
                {
                    "itemIdentifier": message_id,
                }
            )

    return {
        "batchItemFailures": failures,
    }


def lambda_handler(event, context):
    processor = build_processor()

    return process_sqs_event(
        event=event,
        processor=processor,
    )