import uuid

from sqlalchemy.orm import Session

from app.models.attendance import Attendance
from app.models.audit_log import AuditAction, AuditLog
from app.repositories import audit_log_repository


def serialize_attendance(attendance: Attendance) -> dict:
    return {
        "attendance_date": attendance.attendance_date.isoformat(),
        "worker_name": attendance.worker_name,
        "input_parts": float(attendance.input_parts),
        "total_working_hours": float(attendance.total_working_hours),
        "machine_stopped_time": float(attendance.machine_stopped_time),
        "attendance_status": attendance.attendance_status.value,
        "remarks": attendance.remarks,
    }


def record_created(db: Session, attendance: Attendance, *, changed_by: uuid.UUID) -> None:
    log = AuditLog(
        attendance_id=attendance.id,
        action=AuditAction.CREATED,
        old_data=None,
        new_data=serialize_attendance(attendance),
        changed_by=changed_by,
    )
    audit_log_repository.create(db, log)


def record_updated(db: Session, attendance_id: uuid.UUID, old_data: dict, new_data: dict, *, changed_by: uuid.UUID) -> None:
    changed_old = {k: v for k, v in old_data.items() if new_data.get(k) != v}
    changed_new = {k: new_data[k] for k in changed_old}
    if not changed_old:
        return
    log = AuditLog(
        attendance_id=attendance_id,
        action=AuditAction.UPDATED,
        old_data=changed_old,
        new_data=changed_new,
        changed_by=changed_by,
    )
    audit_log_repository.create(db, log)


def record_deleted(db: Session, attendance: Attendance, *, changed_by: uuid.UUID) -> None:
    log = AuditLog(
        attendance_id=attendance.id,
        action=AuditAction.DELETED,
        old_data=serialize_attendance(attendance),
        new_data=None,
        changed_by=changed_by,
    )
    audit_log_repository.create(db, log)
