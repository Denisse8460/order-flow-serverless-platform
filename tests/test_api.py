from fastapi.testclient import TestClient

from src.api.app import create_app
from src.repositories.in_memory_order_repository import (
    InMemoryOrderRepository,
)
from src.services.order_queue import OrderPriorityQueue
from src.services.order_service import OrderService


def create_test_client():
    repository = InMemoryOrderRepository()
    queue = OrderPriorityQueue()

    service = OrderService(
        repository=repository,
        queue=queue,
    )

    app = create_app(service)

    return TestClient(app)


def create_sample_order(client):
    return client.post(
        "/orders",
        json={
            "customer_id": "CUSTOMER-001",
            "items": [
                {
                    "product_id": "PRODUCT-001",
                    "quantity": 2,
                    "unit_price": 100.0,
                }
            ],
            "is_prime": True,
            "delivery_type": "same_day",
        },
    )


def test_health_check():
    client = create_test_client()

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "healthy"
    }


def test_create_order():
    client = create_test_client()

    response = create_sample_order(client)

    assert response.status_code == 201

    body = response.json()

    assert body["customer_id"] == "CUSTOMER-001"
    assert body["status"] == "PENDING"
    assert body["total"] == 200.0
    assert body["priority_score"] == 70


def test_list_orders():
    client = create_test_client()

    create_sample_order(client)

    response = client.get("/orders")

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_get_order():
    client = create_test_client()

    create_response = create_sample_order(client)

    order_id = create_response.json()["order_id"]

    response = client.get(
        f"/orders/{order_id}"
    )

    assert response.status_code == 200
    assert response.json()["order_id"] == order_id


def test_update_order_status():
    client = create_test_client()

    create_response = create_sample_order(client)

    order_id = create_response.json()["order_id"]

    response = client.patch(
        f"/orders/{order_id}/status",
        json={
            "status": "PROCESSING"
        },
    )

    assert response.status_code == 200
    assert response.json()["status"] == "PROCESSING"


def test_unknown_order_returns_404():
    client = create_test_client()

    response = client.get(
        "/orders/DOES-NOT-EXIST"
    )

    assert response.status_code == 404


def test_invalid_quantity_returns_422():
    client = create_test_client()

    response = client.post(
        "/orders",
        json={
            "customer_id": "CUSTOMER-001",
            "items": [
                {
                    "product_id": "PRODUCT-001",
                    "quantity": -5,
                    "unit_price": 100.0,
                }
            ],
        },
    )

    assert response.status_code == 422


def test_invalid_delivery_type_returns_422():
    client = create_test_client()

    response = client.post(
        "/orders",
        json={
            "customer_id": "CUSTOMER-001",
            "items": [
                {
                    "product_id": "PRODUCT-001",
                    "quantity": 1,
                    "unit_price": 100.0,
                }
            ],
            "delivery_type": "teleport",
        },
    )

    assert response.status_code == 422