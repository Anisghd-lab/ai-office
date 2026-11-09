import pytest
from unittest.mock import AsyncMock, patch
from app.scheduler.engine import ExecutiveScheduler
from app.database.connection import db_manager


@pytest.mark.asyncio
async def test_scheduler_timezone():
    scheduler = ExecutiveScheduler("Africa/Algiers")
    algiers_now = scheduler.get_current_algiers_time()
    assert algiers_now.tzinfo is not None
    assert str(algiers_now.tzinfo) == "Africa/Algiers"


@pytest.mark.asyncio
async def test_daily_briefing_execution_and_deduplication():
    scheduler = ExecutiveScheduler("Africa/Algiers")
    
    # Clean previous test artifacts for deterministic test run
    with db_manager.session() as conn:
        conn.execute("DELETE FROM reports WHERE report_type = 'DAILY_BRIEFING';")
    
    # First execution (real call inserts into reports)
    res1 = await scheduler.execute_daily_briefing()
    assert "AI OFFICE EXECUTIVE BRIEFING FOR HUMAN OWNER" in res1
    
    # Second execution on same date should skip duplicate
    res2 = await scheduler.execute_daily_briefing()
    assert res2 == "DUPLICATE_SKIPPED"


@pytest.mark.asyncio
async def test_sunday_board_meeting_and_deduplication():
    scheduler = ExecutiveScheduler("Africa/Algiers")
    
    # First execution
    res1 = await scheduler.execute_sunday_board_meeting()
    assert res1["status"] == "CONCLUDED"
    assert "meeting_id" in res1
    assert "EXECUTIVE BOARD MEETING MINUTES" in res1["minutes"]
    
    # Verify in DB
    with db_manager.session() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT status, minutes FROM executive_meetings WHERE id = ?;", (res1["meeting_id"],))
        row = cursor.fetchone()
        assert row is not None
        assert row[0] == "CONCLUDED"
        
    # Second execution in same week should skip duplicate
    res2 = await scheduler.execute_sunday_board_meeting()
    assert res2["status"] == "DUPLICATE_SKIPPED"


@pytest.mark.asyncio
async def test_library_hour():
    scheduler = ExecutiveScheduler("Africa/Algiers")
    
    inserted = await scheduler.execute_library_hour()
    assert inserted >= 3
    
    with db_manager.session() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT count(*) FROM knowledge_items WHERE provenance = 'weekly-library-hour';")
        count = cursor.fetchone()[0]
        assert count >= 3
