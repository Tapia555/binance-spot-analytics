from __future__ import annotations

from typing import Any

import pandas as pd

CANDLE_COLUMNS = [
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


def klines_to_dataframe(klines: list[list[Any]]) -> pd.DataFrame:
    frame = pd.DataFrame(klines, columns=CANDLE_COLUMNS)

    frame["open_time"] = pd.to_datetime(
        frame["open_time"],
        unit="ms",
        utc=True,
    )
    frame["close_time"] = pd.to_datetime(
        frame["close_time"],
        unit="ms",
        utc=True,
    )

    numeric_columns = [
        "open",
        "high",
        "low",
        "close",
        "volume",
        "quote_asset_volume",
        "taker_buy_base_volume",
        "taker_buy_quote_volume",
    ]

    frame[numeric_columns] = frame[numeric_columns].astype(float)
    frame["trades"] = frame["trades"].astype(int)

    return frame
