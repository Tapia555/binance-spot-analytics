from strategy.ma_crossover_strategy import MACrossoverStrategy


def test_explain_returns_internal_state():
    strat = MACrossoverStrategy(
        fast_period=3, slow_period=5, trend_period=10, rsi_period=14
    )
    closes = [100] * 10 + [
        99,
        99,
        100,
        101,
        102,
        103,
        104,
        105,
        106,
        107,
        108,
        109,
        110,
        111,
        112,
    ]

    dbg = strat.explain(closes)

    assert dbg.price == closes[-1]
    assert dbg.fast_now > 0
    assert dbg.slow_now > 0
    assert isinstance(dbg.prev_state, bool)
    assert isinstance(dbg.now_state, bool)
    assert 0 <= dbg.rsi <= 100
