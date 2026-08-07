import pandas as pd
import pytest

from src.indicators.atr import atr


def test_atr():
    high = pd.Series([12.0, 14.0, 13.0, 16.0])
    low = pd.Series([10.0, 11.0, 11.0, 13.0])
    close = pd.Series([11.0, 13.0, 12.0, 15.0])

    result = atr(high, low, close, period=3)

    assert result.iloc[0] != result.iloc[0]
    assert result.iloc[1] != result.iloc[1]
    assert result.iloc[2] == pytest.approx(2.3333333333)
    assert result.iloc[3] == pytest.approx(3.0)


def test_atr_rejects_invalid_period():
    values = pd.Series([1.0, 2.0, 3.0])

    with pytest.raises(ValueError):
        atr(values, values, values, period=0)
