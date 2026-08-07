from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class OrderSide(str, Enum):
    BUY = "BUY"
    SELL = "SELL"


@dataclass(frozen=True)
class Fill:
    side: OrderSide
    price: float
    quantity: float
    fee: float


class PaperBroker:
    def __init__(
        self,
        quote_balance: float = 1000.0,
        base_balance: float = 0.0,
        fee_rate: float = 0.001,
    ) -> None:
        if quote_balance < 0:
            raise ValueError("quote_balance must not be negative")

        if base_balance < 0:
            raise ValueError("base_balance must not be negative")

        if fee_rate < 0:
            raise ValueError("fee_rate must not be negative")

        self.quote_balance = quote_balance
        self.base_balance = base_balance
        self.fee_rate = fee_rate

    def buy(self, price: float, quantity: float) -> Fill:
        self._validate_order(price, quantity)

        gross = price * quantity
        fee = gross * self.fee_rate
        total = gross + fee

        if total > self.quote_balance:
            raise ValueError("insufficient quote balance")

        self.quote_balance -= total
        self.base_balance += quantity

        return Fill(
            side=OrderSide.BUY,
            price=price,
            quantity=quantity,
            fee=fee,
        )

    def sell(self, price: float, quantity: float) -> Fill:
        self._validate_order(price, quantity)

        if quantity > self.base_balance:
            raise ValueError("insufficient base balance")

        gross = price * quantity
        fee = gross * self.fee_rate
        net = gross - fee

        self.base_balance -= quantity
        self.quote_balance += net

        return Fill(
            side=OrderSide.SELL,
            price=price,
            quantity=quantity,
            fee=fee,
        )

    def equity(self, mark_price: float) -> float:
        if mark_price <= 0:
            raise ValueError("mark_price must be positive")

        return self.quote_balance + self.base_balance * mark_price

    @staticmethod
    def _validate_order(price: float, quantity: float) -> None:
        if price <= 0:
            raise ValueError("price must be positive")

        if quantity <= 0:
            raise ValueError("quantity must be positive")
