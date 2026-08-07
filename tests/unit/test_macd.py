import pandas as pd
import pytest

from src.indicators.macd import macd


def test_macd_columns_and_values():
    close = pd.Series(
        [10.0, 11.0, 12.0, 13.0, 14.0, 15.0],
    )

    result = macd(
        close,
        fast_period=2,
        slow_period=3,
        signal_period=2,
    )

    assert list(result.columns) == ["macd", "signal", "histogram"]
    assert result["macd"].notna().any()
    assert result["signal"].notna().any()

    last = result.iloc[-1]
    assert last["histogram"] == pytest.approx(
        last["macd"] - last["signal"],
    )


def test_macd_rejects_invalid_parameters():
    close = pd.Series([1.0, 2.0, 3.0])

    with pytest.raises(ValueError):
        macd(close, fast_period=0)

    with pytest.raises(ValueError):
        macd(close, fast_period=12, slow_period=12)

    with pytest.raises(ValueError):
        macd(close, signal_period=0)
