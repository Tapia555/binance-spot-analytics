import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    api_key: str
    api_secret: str
    base_url: str
    symbol: str
    testnet: bool


def load_settings() -> Settings:
    return Settings(
        api_key=os.getenv("BINANCE_API_KEY", ""),
        api_secret=os.getenv("BINANCE_API_SECRET", ""),
        base_url=os.getenv(
            "BINANCE_BASE_URL",
            "https://testnet.binance.vision/api",
        ),
        symbol=os.getenv("BINANCE_SYMBOL", "BTCUSDT"),
        testnet=os.getenv("BINANCE_TESTNET", "true").lower() == "true",
    )
