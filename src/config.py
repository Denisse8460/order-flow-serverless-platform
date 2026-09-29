import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    repository_backend: str
    queue_backend: str
    aws_region: str
    dynamodb_table_name: str
    sqs_queue_url: str


def get_settings() -> Settings:
    return Settings(
        repository_backend=os.getenv(
            "ORDERFLOW_REPOSITORY",
            "memory",
        ).lower(),
        queue_backend=os.getenv(
            "ORDERFLOW_QUEUE",
            "memory",
        ).lower(),
        aws_region=os.getenv(
            "ORDERFLOW_AWS_REGION",
            "us-east-1",
        ),
        dynamodb_table_name=os.getenv(
            "ORDERFLOW_DYNAMODB_TABLE",
            "orderflow-orders-dev",
        ),
        sqs_queue_url=os.getenv(
            "ORDERFLOW_SQS_QUEUE_URL",
            "",
        ),
    )