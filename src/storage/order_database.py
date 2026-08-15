from __future__ import annotations

import logging
import sqlite3
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import List, Optional

logger = logging.getLogger(__name__)


@dataclass
class OrderRecord:
    id: int
    symbol: str
    side: str
    order_type: str
    quantity: Decimal
    price: Decimal
    status: str
    created_at: datetime
    updated_at: datetime
    binance_order_id: Optional[int] = None
    strategy_signal: Optional[str] = None


class OrderDatabase:
    """SQLite база для хранения ордеров."""

    def __init__(self, db_path: str = "orders.db") -> None:
        self.db_path = Path(db_path)
        self._init_db()

    def _init_db(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS orders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL,
                    side TEXT NOT NULL,
                    order_type TEXT NOT NULL,
                    quantity TEXT NOT NULL,
                    price TEXT NOT NULL,
                    status TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    binance_order_id INTEGER,
                    strategy_signal TEXT
                )
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_symbol ON orders(symbol)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_status ON orders(status)")
            conn.commit()

    def insert(
        self,
        symbol: str,
        side: str,
        order_type: str,
        quantity: Decimal,
        price: Decimal,
        strategy_signal: Optional[str] = None,
    ) -> int:
        now = datetime.utcnow().isoformat()
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                """
                INSERT INTO orders (symbol, side, order_type, quantity, price, status, created_at, updated_at, strategy_signal)
                VALUES (?, ?, ?, ?, ?, 'PENDING', ?, ?, ?)
                """,
                (symbol, side, order_type, str(quantity), str(price), now, now, strategy_signal),
            )
            conn.commit()
            order_id = cursor.lastrowid
            return order_id if order_id is not None else 0

    def update_status(self, order_id: int, status: str, binance_order_id: Optional[int] = None) -> None:
        now = datetime.utcnow().isoformat()
        with sqlite3.connect(self.db_path) as conn:
            if binance_order_id is not None:
                conn.execute(
                    """
                    UPDATE orders
                    SET status = ?, updated_at = ?, binance_order_id = ?
                    WHERE id = ?
                    """,
                    (status, now, binance_order_id, order_id),
                )
            else:
                conn.execute(
                    """
                    UPDATE orders
                    SET status = ?, updated_at = ?
                    WHERE id = ?
                    """,
                    (status, now, order_id),
                )
            conn.commit()

    def get_by_id(self, order_id: int) -> Optional[OrderRecord]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT * FROM orders WHERE id = ?",
                (order_id,),
            )
            row = cursor.fetchone()
            if row is None:
                return None
            return self._row_to_record(row)

    def get_open_orders(self, symbol: Optional[str] = None) -> List[OrderRecord]:
        with sqlite3.connect(self.db_path) as conn:
            if symbol:
                cursor = conn.execute(
                    "SELECT * FROM orders WHERE symbol = ? AND status IN ('PENDING', 'PARTIALLY_FILLED', 'NEW')",
                    (symbol,),
                )
            else:
                cursor = conn.execute(
                    "SELECT * FROM orders WHERE status IN ('PENDING', 'PARTIALLY_FILLED', 'NEW')",
                )
            return [self._row_to_record(row) for row in cursor.fetchall()]

    def _row_to_record(self, row: tuple) -> OrderRecord:
        return OrderRecord(
            id=row[0],
            symbol=row[1],
            side=row[2],
            order_type=row[3],
            quantity=Decimal(row[4]),
            price=Decimal(row[5]),
            status=row[6],
            created_at=datetime.fromisoformat(row[7]),
            updated_at=datetime.fromisoformat(row[8]),
            binance_order_id=row[9],
            strategy_signal=row[10],
        )
