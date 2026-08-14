from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from strategy.ma_crossover_strategy import MACrossoverStrategy, StrategyAction


@dataclass(frozen=True)
class BacktestTrade:
    index: int
    action: str
    price: float


@dataclass(frozen=True)
class BacktestResult:
    trades: list[BacktestTrade]
    final_action: str
    num_trades: int
    num_buys: int
    num_sells: int
    win_rate: float
    equity_curve: list[float]
    max_drawdown: float


class BacktestEngine:
    def __init__(self, strategy: MACrossoverStrategy) -> None:
        self.strategy = strategy

    def run(self, symbol: str, closes: Sequence[float]) -> BacktestResult:
        trades: list[BacktestTrade] = []
        equity_curve: list[float] = [1.0]
        equity = 1.0
        entry_price: float | None = None

        for i in range(self.strategy.slow_period + 1, len(closes) + 1):
            window = closes[:i]
            signal = self.strategy.generate(symbol, window)
            price = float(window[-1])

            if signal.action == StrategyAction.BUY and entry_price is None:
                entry_price = price
                trades.append(BacktestTrade(index=i - 1, action="BUY", price=price))
            elif signal.action == StrategyAction.SELL and entry_price is not None:
                pnl = (price - entry_price) / entry_price
                equity *= 1.0 + pnl
                trades.append(BacktestTrade(index=i - 1, action="SELL", price=price))
                entry_price = None
                equity_curve.append(equity)
            else:
                equity_curve.append(equity)

        num_buys = sum(1 for t in trades if t.action == "BUY")
        num_sells = sum(1 for t in trades if t.action == "SELL")
        num_trades = len(trades)
        win_rate = (num_buys / num_trades) if num_trades else 0.0
        final_action = trades[-1].action if trades else StrategyAction.HOLD.value
        max_drawdown = self._max_drawdown(equity_curve)

        return BacktestResult(
            trades=trades,
            final_action=final_action,
            num_trades=num_trades,
            num_buys=num_buys,
            num_sells=num_sells,
            win_rate=win_rate,
            equity_curve=equity_curve,
            max_drawdown=max_drawdown,
        )

    @staticmethod
    def _max_drawdown(equity_curve: Sequence[float]) -> float:
        peak = equity_curve[0] if equity_curve else 1.0
        max_dd = 0.0
        for equity in equity_curve:
            if equity > peak:
                peak = equity
            if peak > 0:
                dd = (peak - equity) / peak
                if dd > max_dd:
                    max_dd = dd
        return max_dd
