from __future__ import annotations

import pandas as pd

from data.kline_stream import Kline


class CandleStore:
    def __init__(
        self,
        frame: pd.DataFrame | None = None,
        max_size: int = 500,
    ) -> None:
        if max_size <= 0:
            raise ValueError("max_size must be positive")

        self.max_size = max_size

        if frame is None:
            self.frame = pd.DataFrame(
                columns=[
                    "open_time",
                    "close_time",
                    "open",
                    "high",
                    "low",
                    "close",
                    "volume",
                ]
            )
        else:
            self.frame = frame.copy().tail(max_size)

    def add(self, kline: Kline) -> None:
        if not kline.closed:
            return

        row = pd.DataFrame.from_records(
            [
                {
                    "open_time": pd.to_datetime(
                        kline.open_time,
                        unit="ms",
                        utc=True,
                    ),
                    "close_time": pd.to_datetime(
                        kline.close_time,
                        unit="ms",
                        utc=True,
                    ),
                    "open": kline.open,
                    "high": kline.high,
                    "low": kline.low,
                    "close": kline.close,
                    "volume": kline.volume,
                }
            ]
        )

        self.frame = pd.concat(
            [self.frame, row],
            ignore_index=True,
        )

        self.frame = (
            self.frame
            .drop_duplicates(subset=["open_time"], keep="last")
            .sort_values("open_time")
            .tail(self.max_size)
            .reset_index(drop=True)
        )

    def closes(self) -> pd.Series:
        return self.frame["close"].astype(float)

    def latest(self) -> pd.Series:
        if self.frame.empty:
            raise ValueError("candle store is empty")

        return self.frame.iloc[-1]
