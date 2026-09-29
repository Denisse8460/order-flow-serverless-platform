from src.handlers.process_order_handler import (
    process_sqs_event,
)


class FakeProcessor:
    def __init__(
        self,
        fail_order_id=None,
    ):
        self.processed_events = []
        self.fail_order_id = (
            fail_order_id
        )

    def process(
        self,
        event,
    ):
        if (
            event.get("order_id")
            == self.fail_order_id
        ):
            raise RuntimeError(
                "Simulated processing error."
            )

        self.processed_events.append(
            event
        )


def test_process_sqs_event_success():
    processor = FakeProcessor()

    event = {
        "Records": [
            {
                "messageId": "MESSAGE-001",
                "body": (
                    '{"event_type":"OrderCreated",'
                    '"order_id":"ORDER-001"}'
                ),
            }
        ]
    }

    response = process_sqs_event(
        event=event,
        processor=processor,
    )

    assert response == {
        "batchItemFailures": []
    }

    assert len(
        processor.processed_events
    ) == 1

    assert (
        processor.processed_events[0][
            "order_id"
        ]
        == "ORDER-001"
    )


def test_failed_message_is_reported():
    processor = FakeProcessor(
        fail_order_id="ORDER-002"
    )

    event = {
        "Records": [
            {
                "messageId": "MESSAGE-002",
                "body": (
                    '{"event_type":"OrderCreated",'
                    '"order_id":"ORDER-002"}'
                ),
            }
        ]
    }

    response = process_sqs_event(
        event=event,
        processor=processor,
    )

    assert response == {
        "batchItemFailures": [
            {
                "itemIdentifier": (
                    "MESSAGE-002"
                )
            }
        ]
    }


def test_only_failed_messages_are_returned():
    processor = FakeProcessor(
        fail_order_id="ORDER-002"
    )

    event = {
        "Records": [
            {
                "messageId": "MESSAGE-001",
                "body": (
                    '{"event_type":"OrderCreated",'
                    '"order_id":"ORDER-001"}'
                ),
            },
            {
                "messageId": "MESSAGE-002",
                "body": (
                    '{"event_type":"OrderCreated",'
                    '"order_id":"ORDER-002"}'
                ),
            },
        ]
    }

    response = process_sqs_event(
        event=event,
        processor=processor,
    )

    assert response == {
        "batchItemFailures": [
            {
                "itemIdentifier": (
                    "MESSAGE-002"
                )
            }
        ]
    }

    assert len(
        processor.processed_events
    ) == 1