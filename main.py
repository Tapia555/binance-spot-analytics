import sys
import os
from pathlib import Path

# Debug
print(f"PWD: {os.getcwd()}")
print(f"__file__: {__file__}")
print(f"src exists: {Path('src').exists()}")
if Path('src').exists():
    print(f"src/data exists: {Path('src/data').exists()}")
    print(f"src files: {list(Path('src').iterdir())}")

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))
print(f"sys.path[0]: {sys.path[0]}")

import asyncio
import logging
from dotenv import load_dotenv

load_dotenv()

# Try imports
try:
    from config import load_config
    print("✅ config loaded")
except ImportError as e:
    print(f"❌ config: {e}")

try:
    from data.kline_collector import KlineCollector
    print("✅ data.kline_collector loaded")
except ImportError as e:
    print(f"❌ data.kline_collector: {e}")
    # Try alternative
    try:
        import src.data.kline_collector as kc
        print(f"✅ src.data.kline_collector loaded: {kc}")
    except ImportError as e2:
        print(f"❌ src.data.kline_collector: {e2}")

# ... остальной код ...
