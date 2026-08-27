import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

import asyncio
import logging
from dotenv import load_dotenv

load_dotenv()

from config import load_config
from data.kline_stream import KlineStream, Kline
from strategy.ma_crossover_strategy import MACrossoverStrategy
from execution.binance_testnet import BinanceTestnetClient
from storage.order_database import OrderDatabase
from tg.notifier import TelegramNotifier
from tg.bot_handler import TelegramBotHandler

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(), logging.FileHandler("bot.log")]
)
logger = logging.getLogger(__name__)


class TradingBot:
    def __init__(self, config):
        self.config = config
        self.is_running = False
        self.kline_stream = KlineStream(
            symbol=config.bot.symbol,
            interval="1m"
        )
        self.strategy = MACrossoverStrategy(
            fast_period=config.strategy.fast_period,
            slow_period=config.strategy.slow_period,
            trend_period=config.strategy.trend_period,
            rsi_period=config.strategy.rsi_period,
        )
        self.executor = BinanceTestnetClient(config)
        self.db = OrderDatabase()
        self.closes = []
        self.trades_count = 0
        self.trading_task = None
        
        self.notifier = TelegramNotifier(
            bot_token=config.telegram.bot_token,
            chat_id=config.telegram.chat_id,
            enabled=config.telegram.enabled,
        )
        
        self.bot_handler = TelegramBotHandler(
            bot_token=config.telegram.bot_token,
            on_start=self.start_trading,
            on_stop=self.stop_trading,
            on_status=self.get_status,
        )

    async def start_trading(self):
        if self.is_running:
            logger.info("Already running")
            return
        
        self.is_running = True
        logger.info("Starting trading...")
        self.notifier.notify_start()
        
        async def on_kline(kline: Kline):
            if kline.closed:
                self.closes.append(kline.close)
                logger.info(f"Kline: {kline.close}")
                
                signal = self.strategy.generate(
                    symbol=self.config.bot.symbol,
                    closes=self.closes
                )
                if signal.action.value != "HOLD":
                    logger.info(f"Signal: {signal.action.value} - {signal.reason}")
                    self.notifier.notify_trade(
                        action=signal.action.value,
                        symbol=signal.symbol,
                        price=self.closes[-1],
                        amount=0.001,
                        reason=signal.reason,
                    )
                    self.db.save(signal)
                    self.trades_count += 1
        
        self.trading_task = asyncio.create_task(self.kline_stream.listen(on_kline))

    async def stop_trading(self):
        self.is_running = False
        logger.info("Stopping trading...")
        self.notifier.notify_stop()
        
        if self.trading_task:
            self.trading_task.cancel()

    async def get_status(self) -> str:
        return (
            f"{'Running' if self.is_running else 'Stopped'}\n"
            f"Symbol: {self.config.bot.symbol}\n"
            f"Trades: {self.trades_count}"
        )

    async def run(self):
        # Start Telegram bot
        await self.bot_handler.run()


async def main():
    logger.info("Starting crypto bot...")
    config = load_config()
    
    bot = TradingBot(config)
    
    # Auto-start trading
    await bot.start_trading()
    
    # Run Telegram bot
    await bot.run()


if __name__ == "__main__":
    asyncio.run(main())
