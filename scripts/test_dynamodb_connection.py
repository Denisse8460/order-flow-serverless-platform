import boto3

from src.domain.order import Order, OrderItem
from src.repositories.dynamodb_order_repository import (
    DynamoDBOrderRepository,
)


def main():
    dynamodb = boto3.resource(
        "dynamodb",
        region_name="us-east-1",
    )

    table = dynamodb.Table(
        "orderflow-orders-dev"
    )

    repository = DynamoDBOrderRepository(
        table=table
    )

    order = Order(
        customer_id="AWS-TEST-CUSTOMER",
        items=[
            OrderItem(
                product_id="AWS-PRODUCT-001",
                quantity=1,
                unit_price=250.0,
            )
        ],
        is_prime=True,
        delivery_type="same_day",
    )

    repository.save(order)

    print(
        "Order saved:",
        order.order_id,
    )

    saved_order = repository.get_by_id(
        order.order_id
    )

    print(
        "Order retrieved:",
        saved_order,
    )


if __name__ == "__main__":
    main()