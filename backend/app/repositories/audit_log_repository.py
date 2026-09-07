import uuid

from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from app.models.audit_log import AuditLog


def create(db: Session, log: AuditLog) -> AuditLog:
    db.add(log)
    db.flush()
    return log


def list_for_attendance(db: Session, attendance_id: uuid.UUID) -> list[AuditLog]:
    stmt = (
        select(AuditLog)
        .options(joinedload(AuditLog.changed_by_user))
        .where(AuditLog.attendance_id == attendance_id)
        .order_by(AuditLog.changed_at.desc())
    )
    return list(db.scalars(stmt))


def list_paginated(db: Session, *, page: int, page_size: int) -> tuple[list[AuditLog], int]:
    total = db.scalar(select(func.count()).select_from(AuditLog)) or 0
    stmt = (
        select(AuditLog)
        .options(joinedload(AuditLog.changed_by_user))
        .order_by(AuditLog.changed_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    items = list(db.scalars(stmt))
    return items, total
