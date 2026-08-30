from __future__ import annotations

import logging
import sqlite3
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import List, Optional, Dict, Any

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


@dataclass
class TradeRecord:
    id: int
    symbol: str
    side: str
    quantity: Decimal
    entry_price: Decimal
    exit_price: Optional[Decimal]
    pnl: Optional[Decimal]
    open_time: datetime
    close_time: Optional[datetime]
    status: str  # 'OPEN' или 'CLOSED'


class OrderDatabase:
    """SQLite база для хранения ордеров и сделок."""

    def __init__(self, db_path: str = "orders.db") -> None:
        self.db_path = Path(db_path)
        self._init_db()

    def _init_db(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            # Таблица ордеров
            conn.execute(
                """
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
            """
            )
            conn.execute("CREATE INDEX IF NOT EXISTS idx_symbol ON orders(symbol)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_status ON orders(status)")
            
            # Таблица сделок (для PNL)
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS trades (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL,
                    side TEXT NOT NULL,
                    quantity TEXT NOT NULL,
                    entry_price TEXT NOT NULL,
                    exit_price TEXT,
                    pnl TEXT,
                    open_time TEXT NOT NULL,
                    close_time TEXT,
                    status TEXT NOT NULL DEFAULT 'OPEN'
                )
            """
            )
            conn.execute("CREATE INDEX IF NOT EXISTS idx_trades_symbol ON trades(symbol)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_trades_status ON trades(status)")
            
            conn.commit()

    # ========== Методы для ордеров ==========
    
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
                (
                    symbol,
                    side,
                    order_type,
                    str(quantity),
                    str(price),
                    now,
                    now,
                    strategy_signal,
                ),
            )
            conn.commit()
            order_id = cursor.lastrowid
            return order_id if order_id is not None else 0

    def update_status(
        self, order_id: int, status: str, binance_order_id: Optional[int] = None
    ) -> None:
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
    
    def get_all(self) -> List[OrderRecord]:
        """Вернуть все ордера"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT * FROM orders")
            return [self._row_to_record(row) for row in cursor.fetchall()]

    # ========== Методы для сделок (trades) ==========
    
    def open_trade(
        self,
        symbol: str,
        side: str,
        quantity: Decimal,
        entry_price: Decimal,
    ) -> int:
        """Открыть сделку"""
        now = datetime.utcnow().isoformat()
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                """
                INSERT INTO trades (symbol, side, quantity, entry_price, status, open_time)
                VALUES (?, ?, ?, ?, 'OPEN', ?)
                """,
                (symbol, side, str(quantity), str(entry_price), now),
            )
            conn.commit()
            trade_id = cursor.lastrowid
            return trade_id if trade_id is not None else 0
    
    def close_trade(
        self,
        trade_id: int,
        exit_price: Decimal,
        pnl: Decimal,
    ) -> None:
        """Закрыть сделку"""
        now = datetime.utcnow().isoformat()
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                UPDATE trades
                SET exit_price = ?, pnl = ?, close_time = ?, status = 'CLOSED'
                WHERE id = ?
                """,
                (str(exit_price), str(pnl), now, trade_id),
            )
            conn.commit()
    
    def get_open_trades(self, symbol: Optional[str] = None) -> List[TradeRecord]:
        """Получить открытые сделки"""
        with sqlite3.connect(self.db_path) as conn:
            if symbol:
                cursor = conn.execute(
                    "SELECT * FROM trades WHERE symbol = ? AND status = 'OPEN'",
                    (symbol,),
                )
            else:
                cursor = conn.execute(
                    "SELECT * FROM trades WHERE status = 'OPEN'",
                )
            return [self._row_to_trade(row) for row in cursor.fetchall()]
    
    def get_recent_trades(self, limit: int = 10) -> List[TradeRecord]:
        """Получить последние закрытые сделки"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT * FROM trades WHERE status = 'CLOSED' ORDER BY close_time DESC LIMIT ?",
                (limit,),
            )
            return [self._row_to_trade(row) for row in cursor.fetchall()]
    
    def _row_to_trade(self, row: tuple) -> TradeRecord:
        return TradeRecord(
            id=row[0],
            symbol=row[1],
            side=row[2],
            quantity=Decimal(row[3]),
            entry_price=Decimal(row[4]),
            exit_price=Decimal(row[5]) if row[5] else None,
            pnl=Decimal(row[6]) if row[6] else None,
            open_time=datetime.fromisoformat(row[7]),
            close_time=datetime.fromisoformat(row[8]) if row[8] else None,
            status=row[9],
        )
    
    def get_pnl_summary(self) -> Dict[str, Any]:
        """Получить PNL сводку"""
        with sqlite3.connect(self.db_path) as conn:
            # PNL за день
            cursor = conn.execute("""
                SELECT SUM(CAST(pnl AS REAL)) FROM trades 
                WHERE close_time >= datetime('now', '-1 day')
                AND pnl IS NOT NULL
            """)
            pnl_day = cursor.fetchone()[0] or 0
            
            # PNL за неделю
            cursor = conn.execute("""
                SELECT SUM(CAST(pnl AS REAL)) FROM trades 
                WHERE close_time >= datetime('now', '-7 days')
                AND pnl IS NOT NULL
            """)
            pnl_week = cursor.fetchone()[0] or 0
            
            # PNL за месяц
            cursor = conn.execute("""
                SELECT SUM(CAST(pnl AS REAL)) FROM trades 
                WHERE close_time >= datetime('now', '-30 days')
                AND pnl IS NOT NULL
            """)
            pnl_month = cursor.fetchone()[0] or 0
            
            # Общий PNL
            cursor = conn.execute("""
                SELECT SUM(CAST(pnl AS REAL)) FROM trades 
                WHERE pnl IS NOT NULL
            """)
            pnl_total = cursor.fetchone()[0] or 0
            
            # Количество сделок
            cursor = conn.execute("""
                SELECT COUNT(*) FROM trades 
                WHERE status = 'CLOSED'
            """)
            total_trades = cursor.fetchone()[0] or 0
            
            return {
                'pnl_day': pnl_day,
                'pnl_week': pnl_week,
                'pnl_month': pnl_month,
                'pnl_total': pnl_total,
                'total_trades': total_trades,
            }
