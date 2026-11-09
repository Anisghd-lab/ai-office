"""Database persistence, WAL mode, migrations, and concurrency tests."""

import sqlite3
import tempfile
from pathlib import Path
import pytest
from app.database.connection import DatabaseManager
from app.database.migrations import MigrationManager


def test_sqlite_wal_pragmas_and_creation():
    with tempfile.NamedTemporaryFile(suffix=".db") as tmp:
        mgr = DatabaseManager(db_path=tmp.name)
        with mgr.session() as conn:
            cursor = conn.cursor()
            cursor.execute("PRAGMA journal_mode;")
            mode = cursor.fetchone()[0]
            assert mode.upper() == "WAL"

            cursor.execute("PRAGMA foreign_keys;")
            fk = cursor.fetchone()[0]
            assert fk == 1


def test_migrations_and_idempotency():
    with tempfile.NamedTemporaryFile(suffix=".db") as tmp:
        mgr = DatabaseManager(db_path=tmp.name)
        migrator = MigrationManager()

        # Run migrations 1st time
        with mgr.session() as conn:
            applied_first = migrator.run_migrations(conn)
            assert len(applied_first) > 0

            # Verify tables exist
            cursor = conn.cursor()
            cursor.execute("SELECT count(*) FROM departments;")
            count = cursor.fetchone()[0]
            assert count == 8  # 8 seeded departments

        # Run migrations 2nd time (should be idempotent)
        with mgr.session() as conn:
            applied_second = migrator.run_migrations(conn)
            assert len(applied_second) == 0


def test_restart_recovery_and_persistence():
    with tempfile.NamedTemporaryFile(suffix=".db") as tmp:
        db_path = tmp.name

        # Session 1: Write state
        mgr1 = DatabaseManager(db_path=db_path)
        with mgr1.session() as conn1:
            MigrationManager().run_migrations(conn1)
            conn1.execute(
                "INSERT INTO tasks (id, title, department_id, status) VALUES ('tsk-persist-01', 'Test Persistence', 'research', 'IN_PROGRESS');"
            )

        # Simulate full process death & restart: instantiate brand new manager
        mgr2 = DatabaseManager(db_path=db_path)
        with mgr2.session() as conn2:
            cursor = conn2.cursor()
            cursor.execute("SELECT title, status FROM tasks WHERE id = 'tsk-persist-01';")
            row = cursor.fetchone()
            assert row is not None
            assert row["title"] == "Test Persistence"
            assert row["status"] == "IN_PROGRESS"


def test_wal_concurrency():
    with tempfile.NamedTemporaryFile(suffix=".db") as tmp:
        mgr = DatabaseManager(db_path=tmp.name)
        with mgr.session() as conn:
            MigrationManager().run_migrations(conn)

        # Open concurrent connection A (reader) and connection B (writer)
        conn_reader = mgr.get_connection()
        conn_writer = mgr.get_connection()

        try:
            # Writer creates records
            conn_writer.execute(
                "INSERT INTO tasks (id, title, department_id, status) VALUES ('tsk-conc-1', 'Concurrent 1', 'technology', 'PENDING');"
            )

            # Reader reads simultaneously without blocking
            cursor = conn_reader.cursor()
            cursor.execute("SELECT count(*) FROM tasks;")
            count = cursor.fetchone()[0]
            assert count >= 1
        finally:
            conn_reader.close()
            conn_writer.close()
