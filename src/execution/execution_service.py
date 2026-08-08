from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from src.execution.binance_testnet import BinanceTestnetClient
from src.execution.order_store import OrderStore
from src.execution.order_validator import validate_limit_order


@dataclass(frozen=True)
class SubmittedOrder:
    symbol: str
    order_id: int
    status: str
    side: str
    quantity: str
    price: str


class ExecutionService:
    def __init__(
        self,
        client: BinanceTestnetClient,
        order_store: OrderStore,
    ) -> None:
        self.client = client
        self.order_store = order_store

    def submit_limit_order(
        self,
        *,
        symbol: str,
        side: str,
        quantity: str,
        price: str,
        filters: dict[str, dict[str, str]],
    ) -> SubmittedOrder:
        validation = validate_limit_order(
            price=price,
            quantity=quantity,
            filters=filters,
        )

        if not validation.valid:
            raise ValueError(
                "Invalid order: "
                + "; ".join(validation.errors)
            )

        payload = self.client.place_limit_order(
            symbol=symbol,
            side=side,
            quantity=quantity,
            price=price,
        )

        return SubmittedOrder(
            symbol=str(payload["symbol"]),
            order_id=int(payload["orderId"]),
            status=str(payload["status"]),
            side=str(payload["side"]),
            quantity=str(payload["origQty"]),
            price=str(payload["price"]),
        )

    def cancel_order(
        self,
        *,
        symbol: str,
        order_id: int,
    ) -> dict[str, Any]:
        return self.client.cancel_order(
            symbol=symbol,
            order_id=order_id,
        )
