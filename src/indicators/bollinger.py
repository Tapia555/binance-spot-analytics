from __future__ import annotations

import pandas as pd


def bollinger_bands(
    close: pd.Series,
    period: int = 20,
    deviations: float = 2.0,
) -> pd.DataFrame:
    if period <= 0:
        raise ValueError("period must be positive")

    if deviations <= 0:
        raise ValueError("deviations must be positive")

    middle = close.rolling(
        window=period,
        min_periods=period,
    ).mean()

    standard_deviation = close.rolling(
        window=period,
        min_periods=period,
    ).std(ddof=1)

    upper = middle + deviations * standard_deviation
    lower = middle - deviations * standard_deviation

    return pd.DataFrame(
        {
            "middle": middle,
            "upper": upper,
            "lower": lower,
        }
    )
