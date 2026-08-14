from __future__ import annotations

from backtest.backtest_engine import BacktestEngine
from strategy.ma_crossover_strategy import MACrossoverStrategy


def test_backtest_engine_detects_trades_and_metrics():
    strategy = MACrossoverStrategy(
        fast_period=3, slow_period=5, trend_period=8, rsi_period=5
    )
    engine = BacktestEngine(strategy=strategy)
    closes = [10, 10, 10, 10, 10, 9, 9, 10, 12, 13, 12, 11, 10, 9, 8]

    result = engine.run("BTCUSDT", closes)

    assert result.num_trades >= 1
    assert result.final_action in {"BUY", "SELL", "HOLD"}
    assert 0.0 <= result.win_rate <= 1.0
    assert len(result.equity_curve) >= 1
    assert 0.0 <= result.max_drawdown <= 1.0


def test_backtest_engine_no_trades_for_flat_series():
    strategy = MACrossoverStrategy(
        fast_period=3, slow_period=5, trend_period=8, rsi_period=5
    )
    engine = BacktestEngine(strategy=strategy)

    result = engine.run("BTCUSDT", [10, 10, 10, 10, 10, 10, 10, 10])

    assert result.trades == []
    assert result.final_action == "HOLD"
    assert result.num_trades == 0
    assert result.num_buys == 0
    assert result.num_sells == 0
    assert result.win_rate == 0.0
    assert result.max_drawdown == 0.0
