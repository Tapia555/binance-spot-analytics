import asyncio
import logging
from decimal import Decimal
from .config import settings
from .storage.order_database import OrderDatabase
from .execution.binance_testnet import BinanceTestnetClient
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
        """Get account balance from Binance Testnet."""
        client = BinanceTestnetClient(
                api_key=settings.binance.api_key,
                secret_key=settings.binance.api_secret,
            )
        try:
            balance = await client.get_account_balance("USDT")
            return (
                f"Свободно: {balance.get('free', '0')} "
                f"USDT\n"
                f"Заблокировано: {balance.get('locked', '0')} "
                f"USDT"
            )
        except Exception:
            logger.exception("Error getting Binance balance")
            return "❌ Не удалось получить баланс Binance"
        finally:
            await client.close()

    async def get_all_assets(self) -> str:
        """Get all non-zero balances."""
        client = BinanceTestnetClient(
            api_key=settings.binance.api_key,
            secret_key=settings.binance.api_secret,
        )
        try:
            account = await client.get_account()
            nonzero = [
                b for b in account.get("balances", [])
                if float(b.get("free", 0)) or float(b.get("locked", 0))
            ]
            if not nonzero:
                return "💰 Нет активов с ненулевым балансом"
            
            result = f"💰 Активы ({len(nonzero)}):\n"
            for b in nonzero[:20]:  # Показать первые 20
                free = float(b.get("free", 0))
                locked = float(b.get("locked", 0))
                if free or locked:
                    result += f"{b['asset']}: {free:.8f} (заблокировано: {locked:.8f})\n"
            
            if len(nonzero) > 20:
                result += f"... и ещё {len(nonzero) - 20} активов"
            
            return result.strip()
        except Exception:
            logger.exception("Error getting all assets")
            return "❌ Не удалось получить активы"
        finally:
            await client.close()

    async def get_market_info(self) -> str:
        """Get market data for BTC/USDT."""
        client = BinanceTestnetClient(
            api_key=settings.binance.api_key,
            secret_key=settings.binance.api_secret,
        )
        try:
            symbol = "BTCUSDT"
            
            # Цена
            ticker = await client.get_ticker_price(symbol)
            price = ticker.get("price", "N/A")
            
            # Свечи
            klines = await client.get_klines(symbol, "1h", 5)
            candles = ""
            for k in reversed(klines[:5]):
                # [open_time, open, high, low, close, volume, ...]
                close = float(k[4])
                candles += f"{close:.2f} "
            
            # Параметры символа
            info = await client.get_exchange_info()
            lot_size = "N/A"
            price_step = "N/A"
            for s in info.get("symbols", []):
                if s.get("symbol") == symbol:
                    for f in s.get("filters", []):
                        if f.get("filterType") == "LOT_SIZE":
                            lot_size = f"{float(f['stepSize']):.8f}"
                        elif f.get("filterType") == "PRICE_FILTER":
                            price_step = f"{float(f['tickSize']):.2f}"
                    break
            
            return (
                f"📊 Рынок {symbol}:\n"
                f"💵 Цена: {price} USDT\n"
                f"📈 Последние 5 свечей (1h): {candles.strip()}\n"
                f"📏 Лот: {lot_size}\n"
                f"📐 Шаг цены: {price_step}"
            )
        except Exception:
            logger.exception("Error getting market info")
            return "❌ Не удалось получить рыночные данные"
        finally:
            await client.close()

    async def test_order_action(self) -> str:
        """Create a test order (not sent to matching engine)."""
        client = BinanceTestnetClient(
            api_key=settings.binance.api_key,
            secret_key=settings.binance.api_secret,
        )
        try:
            symbol = "BTCUSDT"
            
            # Получить текущую цену
            ticker = await client.get_ticker_price(symbol)
            current_price = float(ticker.get("price", 0))
            
            # Цена на 1% ниже
            test_price = current_price * 0.99
            quantity = "0.001"
            
            result = await client.test_order(
                symbol=symbol,
                side="BUY",
                order_type="LIMIT",
                quantity=quantity,
                price=f"{test_price:.2f}",
                time_in_force="GTC",
            )
            
            order_id = result.get("orderId", "N/A")
            status = result.get("status", "N/A")
            
            return (
                f"🧪 Тест ордера:\n"
                f"{symbol} BUY {quantity} @ {test_price:.2f}\n"
                f"Order ID: {order_id}\n"
                f"Статус: {status}\n"
                f"✅ Ордер валиден (не отправлен)"
            )
        except Exception as e:
            logger.exception("Error testing order")
            return f"❌ Ошибка тестового ордера: {e}"
        finally:
            await client.close()

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
            on_assets=self.get_all_assets,
            on_market=self.get_market_info,
            on_test_order=self.test_order_action,
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
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)

    bot = TradingBot()
    
    try:
        asyncio.run(bot.run())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Bot error: {e}")


if __name__ == "__main__":
    main()
