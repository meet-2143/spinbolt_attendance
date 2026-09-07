import uuid
from dataclasses import dataclass
from datetime import date

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, contains_eager

from app.models.attendance import Attendance, AttendanceStatus
from app.models.user import User

SORTABLE_COLUMNS = {
    "attendance_date": Attendance.attendance_date,
    "worker_name": Attendance.worker_name,
    "supervisor_name": User.name,
    "input_parts": Attendance.input_parts,
    "total_working_hours": Attendance.total_working_hours,
    "machine_stopped_time": Attendance.machine_stopped_time,
    "created_at": Attendance.created_at,
}


@dataclass
class AttendanceFilters:
    taker_id: uuid.UUID | None = None
    date_from: date | None = None
    date_to: date | None = None
    status: AttendanceStatus | None = None
    search: str | None = None
    sort_by: str = "attendance_date"
    sort_dir: str = "desc"
    page: int = 1
    page_size: int = 20


def get_by_id(db: Session, attendance_id: uuid.UUID) -> Attendance | None:
    return db.get(Attendance, attendance_id)


def get_active_by_date_worker(db: Session, attendance_date: date, worker_name: str) -> Attendance | None:
    stmt = select(Attendance).where(
        Attendance.attendance_date == attendance_date,
        Attendance.worker_name == worker_name,
        Attendance.deleted_at.is_(None),
    )
    return db.scalar(stmt)


def create(db: Session, attendance: Attendance) -> Attendance:
    db.add(attendance)
    db.flush()
    return attendance


def _base_query():
    return (
        select(Attendance)
        .join(User, Attendance.attendance_taker_id == User.id)
        .options(contains_eager(Attendance.attendance_taker))
        .where(Attendance.deleted_at.is_(None))
    )


def _apply_filters(stmt, filters: AttendanceFilters):
    if filters.taker_id:
        stmt = stmt.where(Attendance.attendance_taker_id == filters.taker_id)
    if filters.date_from:
        stmt = stmt.where(Attendance.attendance_date >= filters.date_from)
    if filters.date_to:
        stmt = stmt.where(Attendance.attendance_date <= filters.date_to)
    if filters.status:
        stmt = stmt.where(Attendance.attendance_status == filters.status)
    if filters.search:
        like = f"%{filters.search}%"
        stmt = stmt.where(or_(Attendance.worker_name.ilike(like), User.name.ilike(like)))
    return stmt


def list_paginated(db: Session, filters: AttendanceFilters) -> tuple[list[Attendance], int]:
    stmt = _apply_filters(_base_query(), filters)

    count_stmt = select(func.count()).select_from(stmt.with_only_columns(Attendance.id).subquery())
    total = db.scalar(count_stmt) or 0

    sort_col = SORTABLE_COLUMNS.get(filters.sort_by, Attendance.attendance_date)
    order = sort_col.asc() if filters.sort_dir == "asc" else sort_col.desc()
    stmt = stmt.order_by(order, Attendance.id).offset((filters.page - 1) * filters.page_size).limit(
        filters.page_size
    )

    items = list(db.scalars(stmt))
    return items, total


def list_all(db: Session, filters: AttendanceFilters, *, limit: int = 5000) -> list[Attendance]:
    """Unpaginated fetch for reports/exports. Bounded by `limit` to stay inside a
    serverless function's execution-time budget on very large date ranges."""
    stmt = _apply_filters(_base_query(), filters)
    stmt = stmt.order_by(Attendance.attendance_date, User.name, Attendance.worker_name).limit(limit)
    return list(db.scalars(stmt))


def distinct_worker_names(db: Session, q: str | None, limit: int = 20) -> list[str]:
    stmt = select(Attendance.worker_name).where(Attendance.deleted_at.is_(None)).distinct()
    if q:
        stmt = stmt.where(Attendance.worker_name.ilike(f"%{q}%"))
    stmt = stmt.order_by(Attendance.worker_name).limit(limit)
    return list(db.scalars(stmt))
