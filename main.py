import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

import asyncio
import logging
from dotenv import load_dotenv

load_dotenv()

from config import load_config
from data.kline_collector import KlineCollector
from strategy.ma_crossover import MACrossoverStrategy
from execution.binance_testnet import BinanceTestnetExecutor
from storage.order_database import OrderDatabase
from notifications.telegram import TelegramNotifier

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('bot.log')
    ]
)
logger = logging.getLogger(__name__)

# ... остальной код ...
