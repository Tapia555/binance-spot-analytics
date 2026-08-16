import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

import asyncio
import logging
from dotenv import load_dotenv

load_dotenv()

from config import load_config
from data.kline_stream import KlineStream
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
    
    kline_stream = KlineStream(
        symbol=config.bot.symbol,
        interval="1m"
    )
    strategy = MACrossoverStrategy()
    executor = BinanceTestnetClient(config)
    db = OrderDatabase()
    
    async def on_kline(kline):
        signal = strategy.update(kline)
        if signal:
            await executor.execute(signal)
            db.save(signal)
    
    await kline_stream.listen(on_kline)

if __name__ == "__main__":
    asyncio.run(main())
