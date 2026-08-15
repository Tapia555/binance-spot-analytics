import sys
import os
from pathlib import Path

# Debug
print(f"Working dir: {os.getcwd()}")
print(f"Files: {os.listdir('.')}")
if Path('src').exists():
    print(f"src files: {os.listdir('src')}")

# Add src to path
src_path = Path(__file__).parent / "src"
if src_path.exists():
    sys.path.insert(0, str(src_path))
    print(f"Added to path: {src_path}")

import asyncio
import logging
from dotenv import load_dotenv

load_dotenv()

try:
    from config import load_config
    from data.kline_collector import KlineCollector
    from strategy.ma_crossover import MACrossoverStrategy
    from execution.binance_testnet import BinanceTestnetExecutor
    from storage.order_database import OrderDatabase
    from notifications.telegram import TelegramNotifier
except ImportError as e:
    print(f"Import error: {e}")
    print(f"sys.path: {sys.path}")
    raise

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
