import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.auth.dependencies import require_admin
from app.database.session import get_db
from app.models.audit_log import AuditLog
from app.repositories import audit_log_repository
from app.schemas.audit_log import AuditLogOut
from app.schemas.common import PagedResponse

router = APIRouter(prefix="/api/audit-logs", tags=["audit-logs"], dependencies=[Depends(require_admin)])


def _build_out(log: AuditLog) -> AuditLogOut:
    return AuditLogOut(
        id=log.id,
        attendance_id=log.attendance_id,
        action=log.action,
        old_data=log.old_data,
        new_data=log.new_data,
        changed_by=log.changed_by,
        changed_by_name=log.changed_by_user.name,
        changed_at=log.changed_at,
    )


@router.get("", response_model=PagedResponse[AuditLogOut])
def list_audit_logs(
    page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100), db: Session = Depends(get_db)
) -> PagedResponse[AuditLogOut]:
    items, total = audit_log_repository.list_paginated(db, page=page, page_size=page_size)
    return PagedResponse(items=[_build_out(i) for i in items], total=total, page=page, page_size=page_size)


@router.get("/{attendance_id}", response_model=list[AuditLogOut])
def list_audit_logs_for_attendance(attendance_id: uuid.UUID, db: Session = Depends(get_db)) -> list[AuditLogOut]:
    items = audit_log_repository.list_for_attendance(db, attendance_id)
    return [_build_out(i) for i in items]
