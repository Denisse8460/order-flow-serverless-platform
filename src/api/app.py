import os

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

from src.api.schemas import (
    OrderCreateRequest,
    OrderItemResponse,
    OrderResponse,
    OrderStatusUpdate,
)
from src.bootstrap import create_order_service
from src.domain.order import Order, OrderItem
from src.services.order_service import OrderNotFoundError, OrderService
from src.services.priority_service import PriorityService


def order_to_response(order: Order) -> OrderResponse:
    return OrderResponse(
        order_id=order.order_id,
        customer_id=order.customer_id,
        items=[
            OrderItemResponse(
                product_id=item.product_id,
                quantity=item.quantity,
                unit_price=item.unit_price,
                subtotal=item.subtotal(),
            )
            for item in order.items
        ],
        is_prime=order.is_prime,
        delivery_type=order.delivery_type,
        status=order.status,
        created_at=order.created_at,
        total=order.total(),
        priority_score=PriorityService.calculate_priority(order),
    )


def create_app(
    service: OrderService | None = None,
) -> FastAPI:
    if service is None:
        service = create_order_service()

    app = FastAPI(
        title="OrderFlow API",
        description="Resilient order processing platform.",
        version="0.1.0",
    )

    allowed_origins = [
        origin.strip()
        for origin in os.getenv(
            "ORDERFLOW_ALLOWED_ORIGINS",
            (
                "http://localhost:5173,"
                "http://127.0.0.1:5173"
            ),
        ).split(",")
        if origin.strip()
    ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health")
    def health_check():
        return {
            "status": "healthy",
        }

    @app.post(
        "/orders",
        response_model=OrderResponse,
        status_code=status.HTTP_201_CREATED,
    )
    def create_order(
        payload: OrderCreateRequest,
    ):
        items = [
            OrderItem(
                product_id=item.product_id,
                quantity=item.quantity,
                unit_price=item.unit_price,
            )
            for item in payload.items
        ]

        order = service.create_order(
            customer_id=payload.customer_id,
            items=items,
            is_prime=payload.is_prime,
            delivery_type=payload.delivery_type,
        )

        return order_to_response(order)

    @app.get(
        "/orders",
        response_model=list[OrderResponse],
    )
    def list_orders():
        orders = service.list_orders()

        return [
            order_to_response(order)
            for order in orders
        ]

    @app.get(
        "/orders/{order_id}",
        response_model=OrderResponse,
    )
    def get_order(
        order_id: str,
    ):
        try:
            order = service.get_order(
                order_id
            )

        except OrderNotFoundError as exc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(exc),
            ) from exc

        return order_to_response(order)

    @app.patch(
        "/orders/{order_id}/status",
        response_model=OrderResponse,
    )
    def update_order_status(
        order_id: str,
        payload: OrderStatusUpdate,
    ):
        try:
            order = service.update_status(
                order_id=order_id,
                status=payload.status,
            )

        except OrderNotFoundError as exc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(exc),
            ) from exc

        return order_to_response(order)

    return app


app = create_app()