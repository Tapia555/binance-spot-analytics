import pandas as pd

from data.candles import klines_to_dataframe


def test_klines_to_dataframe():
    klines = [
        [
            1786121820000,
            "64857.99000000",
            "64859.66000000",
            "64853.20000000",
            "64855.99000000",
            "0.20956000",
            1786121879999,
            "13591.24264870",
            51,
            "0.12036000",
            "7806.01568990",
            "0",
        ]
    ]

    frame = klines_to_dataframe(klines)

    assert len(frame) == 1
    assert list(frame.columns) == [
        "open_time",
        "open",
        "high",
        "low",
        "close",
        "volume",
        "close_time",
        "quote_asset_volume",
        "trades",
        "taker_buy_base_volume",
        "taker_buy_quote_volume",
        "ignore",
    ]
    assert frame.loc[0, "close"] == 64855.99
    assert isinstance(frame.loc[0, "open_time"], pd.Timestamp)
    assert frame.loc[0, "open_time"].tz is not None
