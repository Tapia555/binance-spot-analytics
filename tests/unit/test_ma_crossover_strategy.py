from __future__ import annotations

from strategy.ma_crossover_strategy import MACrossoverStrategy, StrategyAction


def test_generate_returns_hold_when_not_enough_data():
    strat = MACrossoverStrategy(fast_period=3, slow_period=5, trend_period=10, rsi_period=14)
    signal = strat.generate("BTCUSDT", [1, 2, 3, 4, 5])
    assert signal.action == StrategyAction.HOLD
    assert signal.reason == "not_enough_data"


def test_explain_returns_debug_state():
    strat = MACrossoverStrategy(fast_period=3, slow_period=5, trend_period=10, rsi_period=14)
    closes = [100] * 10 + [99, 99, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111]
    debug = strat.explain(closes)

    assert debug.price == 111
    assert debug.trend_ma > 0
    assert debug.rsi >= 50
    assert isinstance(debug.prev_state, bool)
    assert isinstance(debug.now_state, bool)


def test_generate_returns_hold_when_filters_block_signal():
    strat = MACrossoverStrategy(fast_period=3, slow_period=5, trend_period=10, rsi_period=14)
    closes = [100] * 10 + [99, 99, 100, 101, 102, 103, 102, 101, 100, 99, 100, 101, 102, 103, 104]
    signal = strat.generate("BTCUSDT", closes)
    assert signal.action == StrategyAction.HOLD
    assert signal.reason == "filtered_or_no_crossover"
