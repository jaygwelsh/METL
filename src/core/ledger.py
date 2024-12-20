import sqlite3
import os
from utils.logger import get_logger

logger = get_logger(__name__)

class Ledger:
    def __init__(self, config):
        self.db_path = config.get("db_path", "ledger.db")
        self._ensure_db()
        self._optimize_db()

    def _ensure_db(self):
        if not os.path.exists(self.db_path):
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            c.execute("""
            CREATE TABLE transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                data TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            """)
            conn.commit()
            conn.close()

    def _optimize_db(self):
        # Apply PRAGMAs for better performance
        # WAL mode improves concurrency
        # synchronous=NORMAL reduces fsync frequency
        # journal_size_limit keeps WAL file small
        # cache_size improves in-memory caching of pages
        with self._get_connection() as conn:
            c = conn.cursor()
            c.execute("PRAGMA journal_mode=WAL;")
            c.execute("PRAGMA synchronous=NORMAL;")
            c.execute("PRAGMA journal_size_limit=1048576;")
            c.execute("PRAGMA cache_size=-2000;")  # approx 2MB cache
            conn.commit()
        self._ensure_index()

    def _ensure_index(self):
        with self._get_connection() as conn:
            c = conn.cursor()
            # Create an index on timestamp to speed up queries by time
            c.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON transactions(timestamp);")
            conn.commit()

    def _get_connection(self):
        # Simple connection pooling: reuse a single connection if possible
        # For high concurrency, consider a connection pool library.
        return sqlite3.connect(self.db_path, isolation_level=None, check_same_thread=False)

    def record_transaction(self, data):
        with self._get_connection() as conn:
            c = conn.cursor()
            c.execute("INSERT INTO transactions (data) VALUES (?)", (data,))
            tx_id = c.lastrowid
            logger.info(f"Recorded transaction {tx_id} in the ledger.")
            return tx_id

    def get_transaction_count(self):
        with self._get_connection() as conn:
            c = conn.cursor()
            c.execute("SELECT COUNT(*) FROM transactions")
            return c.fetchone()[0]
