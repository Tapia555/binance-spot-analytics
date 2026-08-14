from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Sequence


class StrategyAction(str, Enum):
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"


@dataclass(frozen=True)
class StrategySignal:
    action: StrategyAction
    symbol: str
    reason: str


@dataclass(frozen=True)
class StrategyDebug:
    fast_prev: float
    slow_prev: float
    fast_now: float
    slow_now: float
    trend_ma: float
    rsi: float
    price: float
    prev_state: bool
    now_state: bool


class MACrossoverStrategy:
    def __init__(
        self,
        fast_period: int = 9,
        slow_period: int = 21,
        trend_period: int = 200,
        rsi_period: int = 14,
    ) -> None:
        if fast_period >= slow_period:
            raise ValueError("fast_period must be less than slow_period")
        if trend_period <= slow_period:
            raise ValueError("trend_period must be greater than slow_period")
        self.fast_period = fast_period
        self.slow_period = slow_period
        self.trend_period = trend_period
        self.rsi_period = rsi_period

    def explain(self, closes: Sequence[float]) -> StrategyDebug:
        fast_prev = self._sma(closes[-(self.fast_period + 1) : -1])
        slow_prev = self._sma(closes[-(self.slow_period + 1) : -1])
        fast_now = self._sma(closes[-self.fast_period :])
        slow_now = self._sma(closes[-self.slow_period :])
        trend_ma = self._sma(closes[-self.trend_period :])
        rsi = self._rsi(closes[-(self.rsi_period + 1) :])
        price = closes[-1]
        return StrategyDebug(
            fast_prev=fast_prev,
            slow_prev=slow_prev,
            fast_now=fast_now,
            slow_now=slow_now,
            trend_ma=trend_ma,
            rsi=rsi,
            price=price,
            prev_state=fast_prev > slow_prev,
            now_state=fast_now > slow_now,
        )

    def generate(self, symbol: str, closes: Sequence[float]) -> StrategySignal:
        min_len = max(self.trend_period + 1, self.slow_period + 1, self.rsi_period + 1)
        if len(closes) < min_len:
            return StrategySignal(StrategyAction.HOLD, symbol, "not_enough_data")

        debug = self.explain(closes)

        bullish = (
            (not debug.prev_state and debug.now_state)
            and debug.price > debug.trend_ma
            and debug.rsi >= 50
        )
        bearish = (
            (debug.prev_state and not debug.now_state)
            and debug.price < debug.trend_ma
            and debug.rsi <= 50
        )

        if bullish:
            return StrategySignal(
                StrategyAction.BUY, symbol, "bullish_crossover_trend_rsi"
            )
        if bearish:
            return StrategySignal(
                StrategyAction.SELL, symbol, "bearish_crossover_trend_rsi"
            )

        return StrategySignal(StrategyAction.HOLD, symbol, "filtered_or_no_crossover")

    @staticmethod
    def _sma(values: Sequence[float]) -> float:
        return sum(values) / len(values)

    @staticmethod
    def _rsi(values: Sequence[float]) -> float:
        if len(values) < 2:
            return 50.0
        gains = []
        losses = []
        for prev, cur in zip(values[:-1], values[1:]):
            delta = cur - prev
            gains.append(max(delta, 0.0))
            losses.append(max(-delta, 0.0))
        avg_gain = sum(gains) / len(gains)
        avg_loss = sum(losses) / len(losses)
        if avg_loss == 0:
            return 100.0
        rs = avg_gain / avg_loss
        return 100.0 - (100.0 / (1.0 + rs))
