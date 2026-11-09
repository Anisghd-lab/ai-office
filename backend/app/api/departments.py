"""Departments API router."""

import sqlite3
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from app.database.connection import get_db
from app.api.schemas import DepartmentResponse

router = APIRouter(prefix="/departments", tags=["Departments"])


@router.get("", response_model=List[DepartmentResponse])
def list_departments(conn: sqlite3.Connection = Depends(get_db)):
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, director_name, mission, kpi_metrics, status, created_at FROM departments ORDER BY name ASC;")
    rows = cursor.fetchall()
    return [
        DepartmentResponse(
            id=r["id"],
            name=r["name"],
            director_name=r["director_name"],
            mission=r["mission"],
            kpi_metrics=r["kpi_metrics"],
            status=r["status"],
            created_at=str(r["created_at"]),
        )
        for r in rows
    ]


@router.get("/{dept_id}", response_model=DepartmentResponse)
def get_department(dept_id: str, conn: sqlite3.Connection = Depends(get_db)):
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, director_name, mission, kpi_metrics, status, created_at FROM departments WHERE id = ?;", (dept_id.lower(),))
    r = cursor.fetchone()
    if not r:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Department '{dept_id}' not found.")
    return DepartmentResponse(
        id=r["id"],
        name=r["name"],
        director_name=r["director_name"],
        mission=r["mission"],
        kpi_metrics=r["kpi_metrics"],
        status=r["status"],
        created_at=str(r["created_at"]),
    )
