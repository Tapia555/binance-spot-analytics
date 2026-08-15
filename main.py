import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

import asyncio
import logging
from dotenv import load_dotenv

load_dotenv()

from config import load_config
from market_data.ws_market_data_service import WSMarketDataService
from strategy.ma_crossover_strategy import MACrossoverStrategy
from execution.binance_testnet import BinanceTestnetClient
from storage.order_database import OrderDatabase

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler(), logging.FileHandler('bot.log')]
)
logger = logging.getLogger(__name__)

async def main():
    logger.info("🚀 Starting crypto bot...")
    config = load_config()
    market_data = WSMarketDataService(config)
    strategy = MACrossoverStrategy()
    executor = BinanceTestnetClient(config)
    db = OrderDatabase()
    
    await market_data.start()
    
    async for kline in market_data.klines():
        signal = strategy.update(kline)
        if signal:
            await executor.execute(signal)
            db.save(signal)

if __name__ == "__main__":
    asyncio.run(main())
