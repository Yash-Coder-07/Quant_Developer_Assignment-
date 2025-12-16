"""
Database module for storing trade ticks from Binance.
"""
import sqlite3
import threading
from datetime import datetime
from typing import Optional, List, Tuple


class Database:
    """Thread-safe SQLite database for storing trade ticks."""
    
    def __init__(self, db_path: str = "trades.db"):
        self.db_path = db_path
        self.lock = threading.Lock()
        self._init_db()
    
    def _init_db(self):
        """Initialize the database with the ticks table."""
        with self.lock:
            conn = sqlite3.connect(self.db_path, check_same_thread=False)
            cursor = conn.cursor()
            # Enable WAL mode for concurrent reads and writes
            conn.execute("PRAGMA journal_mode=WAL;")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ticks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp REAL NOT NULL,
                    symbol TEXT NOT NULL,
                    price REAL NOT NULL,
                    quantity REAL NOT NULL
                )
            """)
            # Create indexes for faster queries
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_timestamp 
                ON ticks(timestamp)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_symbol 
                ON ticks(symbol)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_timestamp_symbol 
                ON ticks(timestamp, symbol)
            """)
            conn.commit()
            conn.close()
    
    def insert_tick(self, symbol: str, price: float, quantity: float, timestamp: Optional[float] = None):
        """Insert a trade tick into the database."""
        if timestamp is None:
            timestamp = datetime.now().timestamp()
        
        with self.lock:
            conn = sqlite3.connect(self.db_path, check_same_thread=False)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO ticks (timestamp, symbol, price, quantity)
                VALUES (?, ?, ?, ?)
            """, (timestamp, symbol, price, quantity))
            conn.commit()
            conn.close()
    
    def get_ticks(self, symbol: str, minutes: int = 60) -> List[Tuple[float, float, float]]:
        """
        Get ticks for a symbol within the last N minutes.
        Returns list of (timestamp, price, quantity) tuples.
        """
        import time
        cutoff_time = time.time() - (minutes * 60)
        
        with self.lock:
            conn = sqlite3.connect(self.db_path, check_same_thread=False)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT timestamp, price, quantity
                FROM ticks
                WHERE symbol = ? AND timestamp >= ?
                ORDER BY timestamp ASC
            """, (symbol, cutoff_time))
            results = cursor.fetchall()
            conn.close()
            return results
    

    def insert_ticks_batch(self, ticks: List[Tuple[float, str, float, float]]):
        """
        Insert multiple trade ticks into the database in one transaction.
        ticks format: [(timestamp, symbol, price, quantity), ...]
        """
        if not ticks:
            return

        with self.lock:
            conn = sqlite3.connect(self.db_path, check_same_thread=False)
            cursor = conn.cursor()
            
            # This 'executemany' is the secret sauce for speed
            cursor.executemany("""
                INSERT INTO ticks (timestamp, symbol, price, quantity)
                VALUES (?, ?, ?, ?)
            """, ticks)
            
            conn.commit()
            conn.close()


            
    
    def get_all_ticks(self, minutes: int = 60) -> dict:
        """
        Get ticks for all symbols within the last N minutes.
        Returns dict with symbol as key and list of (timestamp, price, quantity) as value.
        """
        import time
        cutoff_time = time.time() - (minutes * 60)
        
        with self.lock:
            conn = sqlite3.connect(self.db_path, check_same_thread=False)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT symbol, timestamp, price, quantity
                FROM ticks
                WHERE timestamp >= ?
                ORDER BY timestamp ASC
            """, (cutoff_time,))
            results = cursor.fetchall()
            conn.close()
            
            # Group by symbol
            ticks_by_symbol = {}
            for symbol, timestamp, price, quantity in results:
                if symbol not in ticks_by_symbol:
                    ticks_by_symbol[symbol] = []
                ticks_by_symbol[symbol].append((timestamp, price, quantity))
            
            return ticks_by_symbol
    
    def cleanup_old_data(self, keep_minutes: int = 1440):
        """Remove data older than keep_minutes (default 24 hours)."""
        import time
        cutoff_time = time.time() - (keep_minutes * 60)
        
        with self.lock:
            conn = sqlite3.connect(self.db_path, check_same_thread=False)
            cursor = conn.cursor()
            cursor.execute("""
                DELETE FROM ticks
                WHERE timestamp < ?
            """, (cutoff_time,))
            conn.commit()
            conn.close()

