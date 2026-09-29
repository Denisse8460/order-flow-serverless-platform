import json

import boto3

REGION = "us-east-1"
QUEUE_NAME = "orderflow-orders-dev"
DLQ_NAME = "orderflow-orders-dlq-dev"


def main():
    sqs = boto3.client(
        "sqs",
        region_name=REGION,
    )

    dlq_response = sqs.create_queue(
        QueueName=DLQ_NAME,
        Attributes={
            "MessageRetentionPeriod": "1209600",
        },
    )

    dlq_url = dlq_response["QueueUrl"]

    dlq_attributes = sqs.get_queue_attributes(
        QueueUrl=dlq_url,
        AttributeNames=[
            "QueueArn",
        ],
    )

    dlq_arn = dlq_attributes[
        "Attributes"
    ]["QueueArn"]

    redrive_policy = {
        "deadLetterTargetArn": dlq_arn,
        "maxReceiveCount": "3",
    }

    queue_response = sqs.create_queue(
        QueueName=QUEUE_NAME,
        Attributes={
            "VisibilityTimeout": "30",
            "ReceiveMessageWaitTimeSeconds": "10",
            "RedrivePolicy": json.dumps(
                redrive_policy
            ),
        },
    )

    queue_url = queue_response["QueueUrl"]

    print("Main queue created:")
    print(queue_url)

    print()

    print("Dead-letter queue created:")
    print(dlq_url)


if __name__ == "__main__":
    main()