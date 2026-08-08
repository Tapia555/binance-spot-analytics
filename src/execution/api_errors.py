from __future__ import annotations


class BinanceApiError(RuntimeError):
    def __init__(
        self,
        code: int | str | None = None,
        message: str = "",
        *,
        status_code: int | None = None,
    ) -> None:
        self.code = code
        self.error_code = code
        self.message = message
        self.status_code = status_code

        super().__init__(
            f"Binance API error {code}: {message}"
        )


class BinanceRateLimitError(BinanceApiError):
    def __init__(
        self,
        code: int | str | None = None,
        message: str = "",
        *,
        status_code: int | None = None,
        retry_after: str | int | None = None,
    ) -> None:
        self.retry_after = (
            int(retry_after)
            if retry_after is not None
            else None
        )

        super().__init__(
            code=code,
            message=message,
            status_code=status_code,
        )
