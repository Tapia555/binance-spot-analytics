from __future__ import annotations
import hashlib
import json

from dataclasses import dataclass
from typing import Any

from execution.binance_testnet import BinanceTestnetClient
from execution.order_store import OrderStore
from execution.order_validator import OrderValidator
from execution.risk_manager import RiskManager
from execution.symbol_rules_service import SymbolRulesService


@dataclass(frozen=True)
class TradeSignal:
    symbol: str
    side: str
    quantity: str
    price: str
    quote_asset: str = "USDT"


class ExecutionService:
    def __init__(
        self,
        client: BinanceTestnetClient,
        store: OrderStore,
        symbol_rules_service: SymbolRulesService,
        order_validator: OrderValidator,
        risk_manager: RiskManager,
    ) -> None:
        self.client = client
        self.store = store
        self.symbol_rules_service = symbol_rules_service
        self.order_validator = order_validator
        self.risk_manager = risk_manager
        self._last_signal_hash: str | None = None
        self._last_signal_hash: str | None = None

    def place_limit_order(self, signal: TradeSignal) -> dict[str, Any]:
        # Проверяем на дубликат сигнала
        signal_dict = {
            "symbol": signal.symbol,
            "side": signal.side,
            "quantity": signal.quantity,
            "price": signal.price,
        }
        signal_hash = hashlib.sha256(json.dumps(signal_dict, sort_keys=True).encode()).hexdigest()
        if self._last_signal_hash == signal_hash:
            return {"status": "duplicate_skipped"}
        self._last_signal_hash = signal_hash

        rules = self.symbol_rules_service.get_rules(signal.symbol)
        self.order_validator.validate(signal.price, signal.quantity, rules)
        self.risk_manager.require_allowed(
            symbol=signal.symbol,
            quote_asset=signal.quote_asset,
            rules=rules,
        )
        placed = self.client.place_limit_order(
            symbol=signal.symbol,
            side=signal.side,
            quantity=signal.quantity,
            price=signal.price,
        )
        order_id = int(placed["orderId"])
        return {
            "order_id": order_id,
            "raw": placed,
        }

    def cancel_order(self, symbol: str, order_id: int) -> dict[str, Any]:
        return self.client.cancel_order(symbol=symbol, order_id=order_id)
