from dataclasses import dataclass
from enum import Enum
from typing import List, Optional

import numpy as np


class StrategyAction(Enum):
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"


@dataclass
class StrategySignal:
    action: StrategyAction
    symbol: str
    price: float
    amount: float
    reason: str


class MACrossoverStrategy:
    def __init__(
        self,
        fast_period: int = 5,  # Уменьшил
        slow_period: int = 10,  # Уменьшил
        trend_period: int = 50,
        rsi_period: int = 14,
    ):
        self.fast_period = fast_period
        self.slow_period = slow_period
        self.trend_period = trend_period
        self.rsi_period = rsi_period

    def _calculate_ma(self, prices: List[float], period: int) -> Optional[float]:
        if len(prices) < period:
            return None
        return float(np.mean(prices[-period:]))

    def _calculate_rsi(self, prices: List[float], period: int = 14) -> Optional[float]:
        if len(prices) < period + 1:
            return None
        
        deltas = np.diff(prices[-period-1:])
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        
        avg_gain = np.mean(gains)
        avg_loss = np.mean(losses)
        
        if avg_loss == 0:
            return 100.0
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return float(rsi)

    def generate(
        self,
        symbol: str,
        closes: List[float],
    ) -> StrategySignal:
        if len(closes) < self.slow_period + 1:
            return StrategySignal(
                action=StrategyAction.HOLD,
                symbol=symbol,
                price=closes[-1] if closes else 0.0,
                amount=0.0,
                reason="Not enough data",
            )
        
        current_price = closes[-1]
        prev_price = closes[-2]
        
        fast_ma = self._calculate_ma(closes, self.fast_period)
        slow_ma = self._calculate_ma(closes, self.slow_period)
        trend_ma = self._calculate_ma(closes, self.trend_period)
        rsi = self._calculate_rsi(closes, self.rsi_period)
        
        if fast_ma is None or slow_ma is None or trend_ma is None:
            return StrategySignal(
                action=StrategyAction.HOLD,
                symbol=symbol,
                price=current_price,
                amount=0.0,
                reason="MA calculation error",
            )
        
        # Сигналы
        if fast_ma > slow_ma and current_price > trend_ma:
            if rsi and rsi < 70:
                return StrategySignal(
                    action=StrategyAction.BUY,
                    symbol=symbol,
                    price=current_price,
                    amount=0.001,
                    reason=f"Fast MA > Slow MA, price > trend MA, RSI={rsi:.1f}",
                )
        
        if fast_ma < slow_ma and current_price < trend_ma:
            if rsi and rsi > 30:
                return StrategySignal(
                    action=StrategyAction.SELL,
                    symbol=symbol,
                    price=current_price,
                    amount=0.001,
                    reason=f"Fast MA < Slow MA, price < trend MA, RSI={rsi:.1f}",
                )
        
        return StrategySignal(
            action=StrategyAction.HOLD,
            symbol=symbol,
            price=current_price,
            amount=0.0,
            reason=f"No signal (fast={fast_ma:.2f}, slow={slow_ma:.2f}, trend={trend_ma:.2f}, rsi={rsi if rsi else 'N/A'})",
        )
