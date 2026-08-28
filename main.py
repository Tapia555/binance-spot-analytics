import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

import asyncio
import logging
import os
from dotenv import load_dotenv

load_dotenv()

from config import load_config
from data.kline_stream import KlineStream, Kline
from strategy.ma_crossover_strategy import MACrossoverStrategy, StrategyAction
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
        
        api_key = hJQSji4DuNxDJ2c0LW("BINANCE_API_KEY")
        secret_key = zBIIsnmAahFtUi7gnM94zgfhKJAtytNBWeER("BINANCE_SECRET_KEY")
        logger.info(f"API Key: {api_key[:10]}..." if api_key else "API Key: None")
        logger.info(f"Secret Key: {secret_key[:10]}..." if secret_key else "Secret Key: None")
        
        self.executor = BinanceTestnetClient(
            base_url=config.bot.base_url,
            api_key=api_key,
            secret_key=secret_key,
        )
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
            on_orders=self.get_orders,
            on_balance=self.get_balance,
            on_trades=self.get_trades,
            on_settings=self.get_settings,
            on_emergency=self.emergency_sell,
            on_restart=self.restart_bot,
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
                if signal.action != StrategyAction.HOLD:
                    logger.info(f"Signal: {signal.action.value} - {signal.reason}")
                    
                    self.notifier.notify_trade(
                        action=signal.action.value,
                        symbol=signal.symbol,
                        price=self.closes[-1],
                        amount=0.001,
                        reason=signal.reason,
                    )
                    
                    try:
                        quantity = "0.001"
                        if signal.action == StrategyAction.BUY:
                            order = await self.executor.create_order(
                                symbol=signal.symbol,
                                side="BUY",
                                order_type="MARKET",
                                quantity=quantity,
                            )
                            logger.info(f"Order executed: {order}")
                        else:
                            order = await self.executor.create_order(
                                symbol=signal.symbol,
                                side="SELL",
                                order_type="MARKET",
                                quantity=quantity,
                            )
                            logger.info(f"Order executed: {order}")
                    except Exception as e:
                        logger.error(f"Order failed: {e}")
                        self.notifier.send_message(f"❌ Order failed: {e}")
                    
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

    async def get_orders(self) -> str:
        try:
            orders = await self.executor.get_open_orders(self.config.bot.symbol)
            if not orders:
                return "No open orders"
            return "\n".join([f"{o['side']} {o['quantity']} @ {o.get('price', 'MARKET')}" for o in orders])
        except Exception as e:
            return f"Error: {e}"

    async def get_balance(self) -> str:
        try:
            account = await self.executor.get_account_balance()
            balances = []
            for b in account.get("balances", []):
                free = float(b["free"])
                if free > 0:
                    balances.append(f"{b['asset']}: {free}")
            return "\n".join(balances) if balances else "No balances"
        except Exception as e:
            logger.error(f"Balance error: {e}")
            return f"Error: {e}"

    async def get_trades(self) -> str:
        try:
            trades = self.db.get_all()
            if not trades:
                return "No trades"
            recent = trades[-10:]
            return "\n".join([f"{t['action']} {t['symbol']} @ {t['price']} - {t['reason']}" for t in recent])
        except Exception as e:
            return f"Error: {e}"

    async def get_settings(self) -> str:
        return (
            f"Fast MA: {self.strategy.fast_period}\n"
            f"Slow MA: {self.strategy.slow_period}\n"
            f"Trend MA: {self.strategy.trend_period}\n"
            f"RSI: {self.strategy.rsi_period}"
        )

    async def emergency_sell(self) -> str:
        try:
            orders = await self.executor.get_open_orders(self.config.bot.symbol)
            for order in orders:
                await self.executor.cancel_order(self.config.bot.symbol, order["orderId"])
            return f"Cancelled {len(orders)} orders"
        except Exception as e:
            return f"Error: {e}"

    async def restart_bot(self):
        logger.info("Restarting bot...")
        await self.stop_trading()
        await asyncio.sleep(2)
        await self.start_trading()

    async def run(self):
        await self.bot_handler.run()


async def main():
    logger.info("Starting crypto bot...")
    config = load_config()
    
    bot = TradingBot(config)
    await bot.run()


if __name__ == "__main__":
    asyncio.run(main())
