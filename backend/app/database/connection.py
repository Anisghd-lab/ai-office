"""SQLite WAL database connection management for AI Office."""

import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Generator, Optional
from app.config import settings
from app.core.logging import logger


class DatabaseManager:
    """Manages SQLite connections with Write-Ahead Logging (WAL) enabled."""

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = Path(db_path or settings.DATABASE_PATH).resolve()
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

    def init_pragmas(self, conn: sqlite3.Connection) -> None:
        """Apply high-performance and resilient PRAGMAs for PRoot ARM64."""
        conn.execute("PRAGMA journal_mode = WAL;")
        conn.execute("PRAGMA synchronous = NORMAL;")
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.execute("PRAGMA busy_timeout = 5000;")
        conn.execute("PRAGMA temp_store = MEMORY;")
        conn.execute("PRAGMA cache_size = -32000;")  # 32MB cache
        conn.row_factory = sqlite3.Row

    def get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(
            str(self.db_path),
            timeout=10.0,
            check_same_thread=False,
            isolation_level=None,  # Autocommit mode; explicit transactions with BEGIN
        )
        self.init_pragmas(conn)
        return conn

    @contextmanager
    def session(self) -> Generator[sqlite3.Connection, None, None]:
        conn = self.get_connection()
        try:
            yield conn
        finally:
            conn.close()


# Default manager instance
db_manager = DatabaseManager()


def get_db() -> Generator[sqlite3.Connection, None, None]:
    """FastAPI dependency for obtaining a database connection."""
    with db_manager.session() as conn:
        yield conn
