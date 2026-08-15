from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import yaml

logger = logging.getLogger(__name__)


@dataclass
class BotConfig:
    symbol: str
    testnet: bool
    base_url: str
    ws_url: str


@dataclass
class StrategyConfig:
    name: str
    fast_period: int
    slow_period: int
    trend_period: int
    rsi_period: int


@dataclass
class RiskConfig:
    max_portfolio_pct: float
    max_loss_per_trade_pct: float
    stop_loss_pct: float
    take_profit_pct: float


@dataclass
class ExecutionConfig:
    timeout: float
    max_retries: int
    retry_delay: float


@dataclass
class TelegramConfig:
    enabled: bool
    bot_token: Optional[str]
    chat_id: Optional[str]


@dataclass
class Settings:
    bot: BotConfig
    strategy: StrategyConfig
    risk: RiskConfig
    execution: ExecutionConfig
    telegram: TelegramConfig
    log_level: str
    log_file: str


def load_config(config_path: str = "config.yaml") -> Settings:
    """Загружает конфиг из YAML файла."""
    path = Path(config_path)

    if not path.exists():
        logger.warning(f"Config file {config_path} not found, using defaults")
        return _default_settings()

    with open(path, "r") as f:
        data = yaml.safe_load(f)

    return Settings(
        bot=BotConfig(
            symbol=data.get("bot", {}).get("symbol", "BTCUSDT"),
            testnet=data.get("bot", {}).get("testnet", True),
            base_url=data.get("bot", {}).get(
                "base_url", "https://testnet.binance.vision"
            ),
            ws_url=data.get("bot", {}).get(
                "ws_url", "wss://stream.testnet.binance.vision/ws"
            ),
        ),
        strategy=StrategyConfig(
            name=data.get("strategy", {}).get("name", "ma_crossover"),
            fast_period=data.get("strategy", {}).get("fast_period", 10),
            slow_period=data.get("strategy", {}).get("slow_period", 20),
            trend_period=data.get("strategy", {}).get("trend_period", 200),
            rsi_period=data.get("strategy", {}).get("rsi_period", 14),
        ),
        risk=RiskConfig(
            max_portfolio_pct=data.get("risk", {}).get("max_portfolio_pct", 0.10),
            max_loss_per_trade_pct=data.get("risk", {}).get(
                "max_loss_per_trade_pct", 0.02
            ),
            stop_loss_pct=data.get("risk", {}).get("stop_loss_pct", 0.02),
            take_profit_pct=data.get("risk", {}).get("take_profit_pct", 0.04),
        ),
        execution=ExecutionConfig(
            timeout=data.get("execution", {}).get("timeout", 10.0),
            max_retries=data.get("execution", {}).get("max_retries", 3),
            retry_delay=data.get("execution", {}).get("retry_delay", 1.0),
        ),
        telegram=TelegramConfig(
            enabled=data.get("telegram", {}).get("enabled", False),
            bot_token=data.get("telegram", {}).get("bot_token"),
            chat_id=data.get("telegram", {}).get("chat_id"),
        ),
        log_level=data.get("logging", {}).get("level", "INFO"),
        log_file=data.get("logging", {}).get("file", "bot.log"),
    )


def _default_settings() -> Settings:
    """Возвращает настройки по умолчанию."""
    return Settings(
        bot=BotConfig(
            symbol="BTCUSDT",
            testnet=True,
            base_url="https://testnet.binance.vision",
            ws_url="wss://stream.testnet.binance.vision/ws",
        ),
        strategy=StrategyConfig(
            name="ma_crossover",
            fast_period=10,
            slow_period=20,
            trend_period=200,
            rsi_period=14,
        ),
        risk=RiskConfig(
            max_portfolio_pct=0.10,
            max_loss_per_trade_pct=0.02,
            stop_loss_pct=0.02,
            take_profit_pct=0.04,
        ),
        execution=ExecutionConfig(
            timeout=10.0,
            max_retries=3,
            retry_delay=1.0,
        ),
        telegram=TelegramConfig(
            enabled=False,
            bot_token=None,
            chat_id=None,
        ),
        log_level="INFO",
        log_file="bot.log",
    )
