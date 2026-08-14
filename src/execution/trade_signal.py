from dataclasses import dataclass


@dataclass(frozen=True)
class TradeSignal:
    symbol: str
    side: str
    quantity: str
    price: str
    quote_asset: str = "USDT"
