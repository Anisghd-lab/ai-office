"""Database migration runner for SQLite WAL."""

import sqlite3
from pathlib import Path
from typing import List, Optional, Tuple
from app.core.logging import logger
from app.database.connection import db_manager


class MigrationManager:
    """Discovers and executes SQL migration scripts against SQLite."""

    def __init__(self, migrations_dir: Optional[Path] = None):
        self.migrations_dir = migrations_dir or (Path(__file__).parent.parent.parent / "migrations")

    def run_migrations(self, conn: Optional[sqlite3.Connection] = None) -> List[str]:
        own_conn = False
        if conn is None:
            conn = db_manager.get_connection()
            own_conn = True

        try:
            # Ensure migration tracking table exists
            conn.execute("""
                CREATE TABLE IF NOT EXISTS schema_migrations (
                    version INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)

            cursor = conn.cursor()
            cursor.execute("SELECT version FROM schema_migrations ORDER BY version ASC;")
            applied_versions = {row[0] for row in cursor.fetchall()}

            migration_files = sorted(self.migrations_dir.glob("*.sql"))
            applied_now = []

            for f in migration_files:
                # Expecting format: 001_name.sql
                parts = f.stem.split("_", 1)
                try:
                    version = int(parts[0])
                except ValueError:
                    continue

                if version not in applied_versions:
                    logger.info(f"Applying database migration: {f.name}")
                    sql_content = f.read_text(encoding="utf-8")
                    conn.executescript(sql_content)
                    conn.execute(
                        "INSERT INTO schema_migrations (version, name) VALUES (?, ?);",
                        (version, f.name),
                    )
                    applied_now.append(f.name)

            return applied_now
        finally:
            if own_conn:
                conn.close()


migration_manager = MigrationManager()
