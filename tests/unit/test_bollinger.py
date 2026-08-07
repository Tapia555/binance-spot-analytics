import pandas as pd
import pytest

from src.indicators.bollinger import bollinger_bands


def test_bollinger_bands():
    close = pd.Series([10.0, 11.0, 12.0, 13.0, 14.0])

    result = bollinger_bands(
        close,
        period=3,
        deviations=2.0,
    )

    assert result.iloc[0].isna().all()
    assert result.iloc[1].isna().all()

    assert result.loc[2, "middle"] == pytest.approx(11.0)
    assert result.loc[2, "upper"] == pytest.approx(13.0)
    assert result.loc[2, "lower"] == pytest.approx(9.0)


def test_bollinger_rejects_invalid_parameters():
    close = pd.Series([1.0, 2.0, 3.0])

    with pytest.raises(ValueError):
        bollinger_bands(close, period=0)

    with pytest.raises(ValueError):
        bollinger_bands(close, deviations=0)
