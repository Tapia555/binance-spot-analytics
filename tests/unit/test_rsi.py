import pandas as pd
import pytest

from indicators.rsi import rsi


def test_rsi_range():
    close = pd.Series(
        [100, 101, 102, 101, 103, 104, 102, 105, 106, 104],
        dtype=float,
    )

    result = rsi(close, period=3)

    valid = result.dropna()

    assert len(valid) > 0
    assert (valid >= 0).all()
    assert (valid <= 100).all()


def test_rsi_rejects_invalid_period():
    close = pd.Series([100.0, 101.0, 102.0])

    with pytest.raises(ValueError):
        rsi(close, period=0)
