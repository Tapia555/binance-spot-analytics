from __future__ import annotations


class BinanceApiError(RuntimeError):
    def __init__(
        self,
        *,
        status_code: int,
        error_code: int | None,
        message: str,
        retry_after: float | None = None,
    ) -> None:
        super().__init__(
            f"Binance API error {error_code}: {message}"
        )
        self.status_code = status_code
        self.error_code = error_code
        self.retry_after = retry_after


class BinanceRateLimitError(BinanceApiError):
    pass
