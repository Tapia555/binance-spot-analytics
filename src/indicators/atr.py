from __future__ import annotations

import pandas as pd


def atr(
    high: pd.Series,
    low: pd.Series,
    close: pd.Series,
    period: int = 14,
) -> pd.Series:
    if period <= 0:
        raise ValueError("period must be positive")

    previous_close = close.shift(1)

    true_range = pd.concat(
        [
            high - low,
            (high - previous_close).abs(),
            (low - previous_close).abs(),
        ],
        axis=1,
    ).max(axis=1)

    return true_range.rolling(
        window=period,
        min_periods=period,
    ).mean()
