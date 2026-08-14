from __future__ import annotations

import pandas as pd

from indicators.exponential_average import ema


def macd(
    close: pd.Series,
    fast_period: int = 12,
    slow_period: int = 26,
    signal_period: int = 9,
) -> pd.DataFrame:
    if fast_period <= 0:
        raise ValueError("fast_period must be positive")

    if slow_period <= 0:
        raise ValueError("slow_period must be positive")

    if signal_period <= 0:
        raise ValueError("signal_period must be positive")

    if fast_period >= slow_period:
        raise ValueError("fast_period must be less than slow_period")

    fast_ema = ema(close, fast_period)
    slow_ema = ema(close, slow_period)

    macd_line = fast_ema - slow_ema
    signal_line = macd_line.ewm(
        span=signal_period,
        adjust=False,
        min_periods=signal_period,
    ).mean()

    histogram = macd_line - signal_line

    return pd.DataFrame(
        {
            "macd": macd_line,
            "signal": signal_line,
            "histogram": histogram,
        }
    )
