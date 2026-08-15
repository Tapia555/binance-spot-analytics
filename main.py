from __future__ import annotations

import asyncio
import logging
import signal
from typing import Optional

from dotenv import load_dotenv

from config import load_config
from data.kline_client import KlineClient
from data.kline_stream import KlineStream, Kline
from execution.binance_testnet import BinanceTestnetClient
from execution.balance_store import BalanceStore
from execution.execution_service import ExecutionService
from execution.order_store import OrderStore
from execution.order_validator import OrderValidator
from execution.position_store import PositionStore
from execution.risk_manager import RiskManager
from execution.symbol_rules_service import SymbolRulesService
from live.live_trading_loop import LiveTradingLoop, KlineUpdate
from reporting.telegram_notifier import TelegramNotifier
from strategy.ma_crossover_strategy import MACrossoverStrategy, StrategyAction
from strategy.trading_engine import TradingEngine

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("bot.log", mode="a"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)

# Хранилище свечей
closes: list[float] = []


async def main() -> None:
    global closes

    load_dotenv()
    config = load_config()

    logger.info(
        f"🤖 Starting bot for {config.bot.symbol} on {'testnet' if config.bot.testnet else 'mainnet'}"
    )
    logger.info(
        f"📊 Strategy: MA Crossover (fast={config.strategy.fast_period}, slow={config.strategy.slow_period}, trend={config.strategy.trend_period})"
    )

    # Клиент Binance
    client = BinanceTestnetClient(
        base_url=config.bot.base_url,
        timeout=config.execution.timeout,
        max_retries=config.execution.max_retries,
        retry_delay=config.execution.retry_delay,
    )

    # Зависимости
    store = OrderStore()
    balances = BalanceStore()
    positions = PositionStore()
    symbol_rules_service = SymbolRulesService(client=client)
    order_validator = OrderValidator()
    risk_manager = RiskManager(
        balances=balances,
        positions=positions,
        max_portfolio_quote_pct=str(config.risk.max_portfolio_pct),
    )

    # Инициализация баланса
    balances.set("USDT", "1000.0", "0.0")

    execution_service = ExecutionService(
        client=client,
        store=store,
        symbol_rules_service=symbol_rules_service,
        order_validator=order_validator,
        risk_manager=risk_manager,
    )

    # Стратегия
    strategy = MACrossoverStrategy(
        fast_period=config.strategy.fast_period,
        slow_period=config.strategy.slow_period,
        trend_period=config.strategy.trend_period,
    )

    # Торговый движок
    engine = TradingEngine(
        strategy=strategy,
        execution_service=execution_service,
    )

    # Цикл торговли
    loop = LiveTradingLoop(trading_engine=engine)

    # Telegram notifier
    telegram = TelegramNotifier(
        bot_token=config.telegram.bot_token,
        chat_id=config.telegram.chat_id,
        enabled=config.telegram.enabled,
    )

    # Загрузка исторических данных
    logger.info("📥 Loading historical klines...")
    kline_client = KlineClient(base_url=config.bot.base_url)
    history = await kline_client.fetch(
        symbol=config.bot.symbol,
        interval="1m",
        limit=200,
    )
    closes = history["close"].tolist()
    logger.info(f"✅ Loaded {len(closes)} historical candles")

    # Предварительное заполнение цикла
    for close in closes:
        update = KlineUpdate(
            symbol=config.bot.symbol,
            interval="1m",
            is_closed=True,
            close=close,
        )
        loop.on_kline(update)

    # WebSocket стрим
    stream = KlineStream(
        symbol=config.bot.symbol,
        interval="1m",
        base_url=config.bot.ws_url,
    )

    stop_event = asyncio.Event()

    def handle_signal(signum, frame):
        logger.info("🛑 Shutdown signal received")
        stop_event.set()

    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)

    async def on_kline(kline: Kline) -> None:
        global closes

        # Обновляем closes
        if kline.closed:
            closes.append(kline.close)
            if len(closes) > 500:
                closes = closes[-500:]
        else:
            if len(closes) > 0:
                closes[-1] = kline.close
            else:
                closes.append(kline.close)

        if kline.closed:
            logger.info(f"✅ Candle closed: {kline.close}")

            # Генерируем сигнал
            signal_result = strategy.generate(config.bot.symbol, closes)
            debug = strategy.explain(closes)

            logger.info(
                f"📊 Strategy: {signal_result.action.value} | "
                f"fast={debug.fast_now:.2f}, slow={debug.slow_now:.2f}, "
                f"trend={debug.trend_ma:.2f}, rsi={debug.rsi:.1f}, "
                f"price={debug.price:.2f}, bullish={debug.now_state}"
            )
            logger.info(f"📝 Reason: {signal_result.reason}")

            # Telegram алерт
            if config.telegram.enabled and signal_result.action != StrategyAction.HOLD:
                await telegram.notify_order(
                    symbol=config.bot.symbol,
                    side=signal_result.action.value,
                    quantity=0.001,
                    price=kline.close,
                    signal=signal_result.reason,
                )

        update = KlineUpdate(
            symbol=config.bot.symbol,
            interval="1m",
            is_closed=kline.closed,
            close=kline.close,
        )

        result = loop.on_kline(update)
        if result:
            logger.info(f"📈 Order placed: {result}")

    logger.info("🚀 Starting kline stream...")
    logger.info("⏳ Waiting for trading signals...")

    try:
        await stream.listen(on_kline=on_kline, stop_event=stop_event)
    except Exception as e:
        logger.error(f"❌ Stream error: {e}")
        if config.telegram.enabled:
            await telegram.notify_error(str(e))
        raise

    logger.info("🏁 Bot stopped")
    await telegram.close()
    await client.close()


if __name__ == "__main__":
    asyncio.run(main())

# Health check for Render
from flask import Flask
import threading

app = Flask(__name__)

@app.route('/health')
def health():
    return 'OK', 200

def run_health_server():
    app.run(host='0.0.0.0', port=8080)

# Запускаем в фоне
threading.Thread(target=run_health_server, daemon=True).start()
