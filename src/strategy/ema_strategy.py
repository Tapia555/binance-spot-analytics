from __future__ import annotations

import pandas as pd

from indicators.exponential_average import ema
from strategy.models import Signal, SignalSide


class EmaStrategy:
    def __init__(
        self,
        fast_period: int = 12,
        slow_period: int = 26,
    ) -> None:
        if fast_period <= 0:
            raise ValueError("fast_period must be positive")

        if slow_period <= 0:
            raise ValueError("slow_period must be positive")

        if fast_period >= slow_period:
            raise ValueError("fast_period must be less than slow_period")

        self.fast_period = fast_period
        self.slow_period = slow_period

    def evaluate(self, close: pd.Series) -> Signal:
        if len(close) < self.slow_period + 1:
            return Signal(
                side=SignalSide.HOLD,
                reason="not enough data",
            )

        fast = ema(close, self.fast_period)
        slow = ema(close, self.slow_period)

        previous_fast = fast.iloc[-2]
        previous_slow = slow.iloc[-2]
        current_fast = fast.iloc[-1]
        current_slow = slow.iloc[-1]
        price = float(close.iloc[-1])

        if previous_fast <= previous_slow and current_fast > current_slow:
            return Signal(
                side=SignalSide.BUY,
                reason="bullish EMA crossover",
                price=price,
                confidence=1.0,
            )

        if previous_fast >= previous_slow and current_fast < current_slow:
            return Signal(
                side=SignalSide.SELL,
                reason="bearish EMA crossover",
                price=price,
                confidence=1.0,
            )

        return Signal(
            side=SignalSide.HOLD,
            reason="no EMA crossover",
            price=price,
            confidence=0.0,
        )
