from __future__ import annotations

import asyncio
import logging
from datetime import datetime

from .config import settings
from .bybit_client import BybitClient
from .indicators import calculate_ma, calculate_rsi
from .strategy import generate_signal
from .telegram import send_telegram_message

logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(settings.log_file),
        logging.StreamHandler(),
    ],
)

logger = logging.getLogger(__name__)


async def main():
    """Основной цикл бота для Bybit."""
    logger.info("Starting Bybit bot...")
    
    client = BybitClient()
    symbol = settings.bot.symbol
    
    # Проверка подключения
    balance = await client.get_balance("USDT")
    logger.info(f"USDT Balance: {balance}")
    
    if balance is None:
        logger.error("Failed to get balance. Check API keys.")
        return
    
    await send_telegram_message(
        f"🚀 Bybit Bot Started\n"
        f"Symbol: {symbol}\n"
        f"Balance: {balance} USDT"
    )
    
    last_trade_time = None
    
    while True:
        try:
            # Получаем свечи
            klines = await client.get_klines(symbol, interval="1", limit=300)
            
            if not klines or len(klines) < settings.strategy.slow_period:
                logger.warning("Not enough data")
                await asyncio.sleep(60)
                continue
            
            # Преобразуем в формат [time, open, high, low, close, volume, ...]
            closes = [float(k[4]) for k in klines]
            highs = [float(k[2]) for k in klines]
            lows = [float(k[3]) for k in klines]
            volumes = [float(k[5]) for k in klines]
            
            # Индикаторы
            fast_ma = calculate_ma(closes, settings.strategy.fast_period)
            slow_ma = calculate_ma(closes, settings.strategy.slow_period)
            trend_ma = calculate_ma(closes, settings.strategy.trend_period)
            rsi = calculate_rsi(closes, settings.strategy.rsi_period)
            
            current_price = closes[-1]
            
            logger.info(
                f"Price: {current_price:.2f} | "
                f"Fast MA: {fast_ma:.2f} | Slow MA: {slow_ma:.2f} | "
                f"Trend MA: {trend_ma:.2f} | RSI: {rsi:.2f}"
            )
            
            # Сигнал
            signal = generate_signal(
                fast_ma=fast_ma,
                slow_ma=slow_ma,
                trend_ma=trend_ma,
                rsi=rsi,
                current_price=current_price,
            )
            
            logger.info(f"Signal: {signal}")
            
            # Торговля
            if signal == "BUY" and last_trade_time != "BUY":
                qty = (balance * settings.risk.max_portfolio_pct) / current_price
                logger.info(f"Placing BUY order: {qty} {symbol}")
                
                order = await client.place_order(
                    symbol=symbol,
                    side="Buy",
                    qty=qty,
                    order_type="Market",
                )
                
                if order:
                    logger.info(f"Order placed: {order}")
                    await send_telegram_message(
                        f"✅ BUY {symbol}\n"
                        f"Price: {current_price:.2f}\n"
                        f"Qty: {qty:.6f}\n"
                        f"Order: {order.get('orderId', 'N/A')}"
                    )
                    last_trade_time = "BUY"
                    
            elif signal == "SELL" and last_trade_time != "SELL":
                logger.info(f"Placing SELL order")
                
                # Получаем баланс монеты
                coin_balance = await client.get_balance(symbol.replace("USDT", ""))
                
                if coin_balance and coin_balance > 0:
                    order = await client.place_order(
                        symbol=symbol,
                        side="Sell",
                        qty=coin_balance,
                        order_type="Market",
                    )
                    
                    if order:
                        logger.info(f"Order placed: {order}")
                        await send_telegram_message(
                            f"✅ SELL {symbol}\n"
                            f"Price: {current_price:.2f}\n"
                            f"Qty: {coin_balance:.6f}\n"
                            f"Order: {order.get('orderId', 'N/A')}"
                        )
                        last_trade_time = "SELL"
            
            await asyncio.sleep(60)  # 1 минута
            
        except KeyboardInterrupt:
            logger.info("Bot stopped by user")
            await send_telegram_message("🛑 Bot stopped")
            break
        except Exception as e:
            logger.error(f"Error in main loop: {e}", exc_info=True)
            await asyncio.sleep(60)


if __name__ == "__main__":
    asyncio.run(main())

# Debug: покажи первые 5 цен
# logger.info(f"First 5 closes: {closes[:5]}")
# logger.info(f"Last 5 closes: {closes[-5:]}")
