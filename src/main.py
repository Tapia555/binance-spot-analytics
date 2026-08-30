import asyncio
import logging
from decimal import Decimal
from .config import settings
from .storage.order_database import OrderDatabase
from .execution.bybit_client import BybitClient
from .tg.bot_handler import TelegramBotHandler

logger = logging.getLogger(__name__)


class TradingBot:
    def __init__(self) -> None:
        self.db = OrderDatabase("data/trades.db")
        self._running = False

    async def start_trading(self) -> None:
        """Start trading"""
        logger.info("Starting trading...")
        self._running = True

    async def stop_trading(self) -> None:
        """Stop trading"""
        logger.info("Stopping trading...")
        self._running = False

    async def get_status(self) -> str:
        """Get bot status"""
        return f"Статус: {'✅ Работает' if self._running else '⏹️ Остановлен'}\nСимвол: {settings.bot.symbol}"

    async def get_orders(self) -> str:
        """Get active orders"""
        try:
            orders = self.db.get_open_orders()
            if not orders:
                return "Нет активных ордеров"
            result = f"Активных ордеров: {len(orders)}\n"
            for order in orders[:5]:
                result += f"\n{order.symbol} {order.side} {order.quantity} @ {order.price}"
            return result
        except Exception as e:
            logger.error(f"Error getting orders: {e}")
            return "❌ Ошибка"

    async def get_balance(self) -> str:
        """Get account balance"""
        return "💰 Баланс: загрузка..."

    async def get_trades(self) -> str:
        """Get recent trades"""
        try:
            trades = self.db.get_recent_trades(limit=10)
            if not trades:
                return "📜 Нет закрытых сделок"
            result = f"Последние сделки ({len(trades)}):\n"
            for trade in trades[:5]:
                pnl_str = f"${float(trade.pnl):.2f}" if trade.pnl else "N/A"
                result += f"\n{trade.symbol} {trade.side} {trade.quantity} | PNL: {pnl_str}"
            return result
        except Exception as e:
            logger.error(f"Error getting trades: {e}")
            return "❌ Ошибка"

    async def get_pnl(self) -> str:
        """Get PNL for different periods"""
        try:
            summary = self.db.get_pnl_summary()
            return (
                f"📊 PNL:\n"
                f"📅 День: ${summary['pnl_day']:.2f}\n"
                f"📅 Неделя: ${summary['pnl_week']:.2f}\n"
                f"📅 Месяц: ${summary['pnl_month']:.2f}\n"
                f"📅 Всего: ${summary['pnl_total']:.2f}\n"
                f"💼 Всего сделок: {summary['total_trades']}"
            )
        except Exception as e:
            logger.error(f"Error getting PNL: {e}")
            return "❌ Ошибка PNL"

    async def get_settings(self) -> str:
        """Get current settings"""
        return (
            f"⚙️ Настройки:\n"
            f"Символ: {settings.bot.symbol}\n"
            f"Testnet: {settings.bot.testnet}"
        )

    async def emergency_stop(self) -> str:
        """Emergency stop"""
        return "🚨 Тревога активирована"

    async def restart_bot(self) -> None:
        """Restart the bot"""
        logger.info("Restart requested")

    async def run(self) -> None:
        """Main bot loop"""
        logger.info("Starting trading bot...")
        
        bot = TelegramBotHandler(
            bot_token=settings.telegram.bot_token,
            on_start=self.start_trading,
            on_stop=self.stop_trading,
            on_status=self.get_status,
            on_orders=self.get_orders,
            on_balance=self.get_balance,
            on_trades=self.get_trades,
            on_settings=self.get_settings,
            on_emergency=self.emergency_stop,
            on_restart=self.restart_bot,
            on_pnl=self.get_pnl,
        )
        
        await bot.run()


def main() -> None:
    """Entry point"""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    
    bot = TradingBot()
    
    try:
        asyncio.run(bot.run())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Bot error: {e}")


if __name__ == "__main__":
    main()
