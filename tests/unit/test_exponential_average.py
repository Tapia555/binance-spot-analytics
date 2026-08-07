import pandas as pd
import pytest

from src.indicators.exponential_average import ema


def test_ema():
    values = pd.Series([10.0, 11.0, 12.0, 13.0, 14.0])

    result = ema(values, period=3)

    assert result.iloc[0] != result.iloc[0]
    assert result.iloc[1] != result.iloc[1]
    assert result.iloc[2] == pytest.approx(11.25)
    assert result.iloc[3] == pytest.approx(12.125)
    assert result.iloc[4] == pytest.approx(13.0625)


def test_ema_rejects_invalid_period():
    with pytest.raises(ValueError):
        ema(pd.Series([1.0, 2.0]), period=0)
