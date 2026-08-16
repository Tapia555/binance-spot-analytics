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

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(), logging.FileHandler("bot.log")]
)
logger = logging.getLogger(__name__)

async def main():
    logger.info("Starting crypto bot...")
    config = load_config()
    
    logger.info(f"Symbol: {config.bot.symbol}")
    logger.info(f"Testnet: {config.bot.testnet}")
    
    kline_stream = KlineStream(
        symbol=config.bot.symbol,
        interval="1m"
    )
    strategy = MACrossoverStrategy(
        fast_period=config.strategy.fast_period,
        slow_period=config.strategy.slow_period,
        trend_period=config.strategy.trend_period,
        rsi_period=config.strategy.rsi_period,
    )
    executor = BinanceTestnetClient(config)
    db = OrderDatabase()
    
    closes = []
    kline_count = 0
    
    async def on_kline(kline: Kline):
        nonlocal kline_count
        kline_count += 1
        
        if kline.closed:
            closes.append(kline.close)
            logger.info(f"Kline #{kline_count}: {kline.close} (closed={kline.closed})")
            
            signal = strategy.generate(symbol=config.bot.symbol, closes=closes)
            if signal.action.value != "HOLD":
                logger.info(f"Signal: {signal.action.value} - {signal.reason}")
                await executor.execute(signal)
                db.save(signal)
    
    await kline_stream.listen(on_kline)

if __name__ == "__main__":
    asyncio.run(main())
