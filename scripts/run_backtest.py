#!/usr/bin/env python3
"""Backtest стратегии MA Crossover на исторических данных."""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from decimal import Decimal
from typing import List, Tuple

from config import load_config
from data.kline_client import KlineClient
from strategy.ma_crossover_strategy import MACrossoverStrategy

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


@dataclass
class BacktestResult:
    total_trades: int
    winning_trades: int
    losing_trades: int
    total_pnl: Decimal
    win_rate: float
    avg_win: Decimal
    avg_loss: Decimal
    max_drawdown: Decimal


async def run_backtest(
    symbol: str = "BTCUSDT",
    interval: str = "1m",
    limit: int = 500,
    fast_period: int = 10,
    slow_period: int = 20,
    trend_period: int = 200,
) -> BacktestResult:
    """Запускает бэктест."""
    logger.info(f"📊 Starting backtest for {symbol}...")

    # Загружаем исторические данные
    client = KlineClient(base_url="https://testnet.binance.vision")
    data = await client.fetch(symbol=symbol, interval=interval, limit=limit)

    closes = data["close"].tolist()
    logger.info(f"✅ Loaded {len(closes)} candles")

    # Инициализируем стратегию
    strategy = MACrossoverStrategy(
        fast_period=fast_period,
        slow_period=slow_period,
        trend_period=trend_period,
    )

    # Симуляция торговли
    position: str | None = None
    entry_price: float | None = None
    trades: List[Tuple[str, float, float]] = []

    for i in range(len(closes)):
        current_closes = closes[: i + 1]

        if len(current_closes) < trend_period:
            continue

        signal = strategy.generate(symbol, current_closes)

        if signal.action.value == "BUY" and position != "BUY":
            if position == "SELL":
                trades.append(("SELL", entry_price, current_closes[-1]))
            position = "BUY"
            entry_price = current_closes[-1]
            logger.info(f"🟢 BUY @ {entry_price:.2f}")

        elif signal.action.value == "SELL" and position != "SELL":
            if position == "BUY":
                trades.append(("BUY", entry_price, current_closes[-1]))
            position = "SELL"
            entry_price = current_closes[-1]
            logger.info(f"🔴 SELL @ {entry_price:.2f}")

    # Закрываем последнюю позицию
    if position and entry_price:
        trades.append((position, entry_price, closes[-1]))

    # Считаем PnL
    pnls: List[Decimal] = []
    for side, entry, exit in trades:
        if side == "BUY":
            pnl = Decimal(str(exit - entry))
        else:
            pnl = Decimal(str(entry - exit))
        pnls.append(pnl)

    total_pnl = sum(pnls)
    winning_trades = [p for p in pnls if p > 0]
    losing_trades = [p for p in pnls if p < 0]

    # Max drawdown
    cumulative = Decimal("0")
    peak = Decimal("0")
    max_drawdown = Decimal("0")
    for pnl in pnls:
        cumulative += pnl
        if cumulative > peak:
            peak = cumulative
        drawdown = peak - cumulative
        if drawdown > max_drawdown:
            max_drawdown = drawdown

    result = BacktestResult(
        total_trades=len(trades),
        winning_trades=len(winning_trades),
        losing_trades=len(losing_trades),
        total_pnl=total_pnl,
        win_rate=len(winning_trades) / len(trades) if trades else 0,
        avg_win=sum(winning_trades) / len(winning_trades) if winning_trades else Decimal("0"),
        avg_loss=sum(losing_trades) / len(losing_trades) if losing_trades else Decimal("0"),
        max_drawdown=max_drawdown,
    )

    return result


def main() -> None:
    config = load_config()

    result = asyncio.run(
        run_backtest(
            symbol=config.bot.symbol,
            fast_period=config.strategy.fast_period,
            slow_period=config.strategy.slow_period,
            trend_period=config.strategy.trend_period,
        )
    )

    print("\n" + "=" * 50)
    print("📊 BACKTEST RESULTS")
    print("=" * 50)
    print(f"Total trades:     {result.total_trades}")
    print(f"Winning trades:   {result.winning_trades}")
    print(f"Losing trades:    {result.losing_trades}")
    print(f"Win rate:         {result.win_rate:.2%}")
    print(f"Total PnL:        ${result.total_pnl:.2f}")
    print(f"Avg win:          ${result.avg_win:.2f}")
    print(f"Avg loss:         ${result.avg_loss:.2f}")
    print(f"Max drawdown:     ${result.max_drawdown:.2f}")
    print("=" * 50)


if __name__ == "__main__":
    main()
