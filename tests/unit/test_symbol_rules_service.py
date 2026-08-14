from __future__ import annotations

from decimal import Decimal

import pytest

from execution.symbol_rules_service import SymbolRulesService


class DummyClient:
    def get_exchange_info(self):
        return {
            "symbols": [
                {
                    "symbol": "BTCUSDT",
                    "filters": [
                        {
                            "filterType": "PRICE_FILTER",
                            "minPrice": "0.01",
                            "maxPrice": "1000000.00",
                            "tickSize": "0.01",
                        },
                        {
                            "filterType": "LOT_SIZE",
                            "minQty": "0.00001000",
                            "maxQty": "1000.00000000",
                            "stepSize": "0.00001000",
                        },
                        {
                            "filterType": "MIN_NOTIONAL",
                            "minNotional": "10.00",
                        },
                    ],
                }
            ]
        }


def test_get_rules_parses_filters():
    service = SymbolRulesService(client=DummyClient())

    rules = service.get_rules("BTCUSDT")

    assert rules.symbol == "BTCUSDT"
    assert rules.min_price == Decimal("0.01")
    assert rules.max_price == Decimal("1000000.00")
    assert rules.tick_size == Decimal("0.01")
    assert rules.min_qty == Decimal("0.00001000")
    assert rules.max_qty == Decimal("1000.00000000")
    assert rules.step_size == Decimal("0.00001000")
    assert rules.min_notional == Decimal("10.00")


def test_get_rules_raises_for_missing_symbol():
    service = SymbolRulesService(client=DummyClient())

    with pytest.raises(ValueError, match="symbol not found"):
        service.get_rules("ETHUSDT")
