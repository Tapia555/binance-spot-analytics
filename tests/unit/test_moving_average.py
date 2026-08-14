import pandas as pd
import pytest

from indicators.moving_average import sma


def test_sma():
    values = pd.Series([10.0, 11.0, 12.0, 13.0, 14.0])

    result = sma(values, period=3)

    assert result.iloc[0] != result.iloc[0]
    assert result.iloc[1] != result.iloc[1]
    assert result.iloc[2] == pytest.approx(11.0)
    assert result.iloc[3] == pytest.approx(12.0)
    assert result.iloc[4] == pytest.approx(13.0)


def test_sma_rejects_invalid_period():
    with pytest.raises(ValueError):
        sma(pd.Series([1.0, 2.0]), period=0)
