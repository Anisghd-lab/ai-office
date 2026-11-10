"""Pytest global configuration and fixtures."""

import os
import tempfile
from pathlib import Path
import pytest
from app.config import settings
from app.database.connection import DatabaseManager, db_manager
from app.database.migrations import MigrationManager


@pytest.fixture(scope="session", autouse=True)
def test_database_session():
    """Create an isolated SQLite database for the test session."""
    tmp_dir = tempfile.mkdtemp()
    test_db_path = str(Path(tmp_dir) / "test_ai_office.db")

    # Override database path in settings and global db_manager
    settings.DATABASE_PATH = test_db_path
    db_manager.db_path = Path(test_db_path)
    db_manager.db_path.parent.mkdir(parents=True, exist_ok=True)

    # Run initial migrations
    with db_manager.session() as conn:
        MigrationManager().run_migrations(conn)

    from app.company.employees import employee_service
    from app.departments.registry import initialize_directors
    initialize_directors()
    employee_service.sync_registry_to_db()

    yield test_db_path
