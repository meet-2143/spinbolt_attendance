import uuid

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.attendance import Attendance
from app.models.user import User, UserRole
from app.repositories import attendance_repository
from app.schemas.attendance import AttendanceCreate, AttendanceOut, AttendanceUpdate, BulkAttendanceRow
from app.services import audit_service
from app.services.exceptions import BulkValidationError, DuplicateAttendanceError


def build_attendance_out(attendance: Attendance) -> AttendanceOut:
    return AttendanceOut(
        id=attendance.id,
        attendance_date=attendance.attendance_date,
        attendance_taker_id=attendance.attendance_taker_id,
        attendance_taker_name=attendance.attendance_taker.name,
        worker_name=attendance.worker_name,
        input_parts=attendance.input_parts,
        total_working_hours=attendance.total_working_hours,
        machine_stopped_time=attendance.machine_stopped_time,
        attendance_status=attendance.attendance_status,
        remarks=attendance.remarks,
        created_at=attendance.created_at,
        updated_at=attendance.updated_at,
        created_by=attendance.created_by,
        updated_by=attendance.updated_by,
    )


def _assert_can_access(current_user: User, attendance: Attendance) -> None:
    if current_user.role == UserRole.SUPERVISOR and attendance.attendance_taker_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this attendance record.",
        )


def get_attendance_or_404(db: Session, attendance_id: uuid.UUID, *, current_user: User) -> Attendance:
    attendance = attendance_repository.get_by_id(db, attendance_id)
    if not attendance or attendance.deleted_at is not None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Attendance record not found.")
    _assert_can_access(current_user, attendance)
    return attendance


def create_attendance(db: Session, *, payload: AttendanceCreate, current_user: User) -> Attendance:
    existing = attendance_repository.get_active_by_date_worker(db, payload.attendance_date, payload.worker_name)
    if existing:
        raise DuplicateAttendanceError(existing.id)

    attendance = Attendance(
        attendance_date=payload.attendance_date,
        attendance_taker_id=current_user.id,
        worker_name=payload.worker_name,
        input_parts=payload.input_parts,
        total_working_hours=payload.total_working_hours,
        machine_stopped_time=payload.machine_stopped_time,
        attendance_status=payload.attendance_status,
        remarks=payload.remarks,
        created_by=current_user.id,
    )
    attendance_repository.create(db, attendance)
    audit_service.record_created(db, attendance, changed_by=current_user.id)
    db.commit()
    db.refresh(attendance)
    return attendance


def update_attendance(
    db: Session, *, attendance_id: uuid.UUID, payload: AttendanceUpdate, current_user: User
) -> Attendance:
    attendance = get_attendance_or_404(db, attendance_id, current_user=current_user)

    if payload.attendance_date != attendance.attendance_date or payload.worker_name != attendance.worker_name:
        existing = attendance_repository.get_active_by_date_worker(db, payload.attendance_date, payload.worker_name)
        if existing and existing.id != attendance.id:
            raise DuplicateAttendanceError(existing.id)

    old_data = audit_service.serialize_attendance(attendance)

    attendance.attendance_date = payload.attendance_date
    attendance.worker_name = payload.worker_name
    attendance.input_parts = payload.input_parts
    attendance.total_working_hours = payload.total_working_hours
    attendance.machine_stopped_time = payload.machine_stopped_time
    attendance.attendance_status = payload.attendance_status
    attendance.remarks = payload.remarks
    attendance.updated_by = current_user.id
    db.flush()

    new_data = audit_service.serialize_attendance(attendance)
    audit_service.record_updated(db, attendance.id, old_data, new_data, changed_by=current_user.id)

    db.commit()
    db.refresh(attendance)
    return attendance


def void_attendance(db: Session, *, attendance_id: uuid.UUID, reason: str, current_user: User) -> None:
    from datetime import datetime, timezone

    attendance = attendance_repository.get_by_id(db, attendance_id)
    if not attendance or attendance.deleted_at is not None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Attendance record not found.")

    audit_service.record_deleted(db, attendance, changed_by=current_user.id)
    attendance.deleted_at = datetime.now(timezone.utc)
    attendance.deleted_by = current_user.id
    attendance.deletion_reason = reason
    db.commit()


def bulk_create_attendance(
    db: Session, *, rows: list[BulkAttendanceRow], current_user: User
) -> list[Attendance]:
    errors: list[dict] = []
    seen: set[tuple] = set()
    for idx, row in enumerate(rows):
        key = (row.attendance_date, row.worker_name)
        if key in seen:
            errors.append(
                {"row": idx, "worker_name": row.worker_name, "message": "Duplicate worker in this submission."}
            )
        seen.add(key)

    created: list[Attendance] = []
    if not errors:
        for idx, row in enumerate(rows):
            existing = attendance_repository.get_active_by_date_worker(db, row.attendance_date, row.worker_name)
            if existing:
                errors.append(
                    {
                        "row": idx,
                        "worker_name": row.worker_name,
                        "message": f"Attendance already exists for {row.worker_name} on {row.attendance_date}.",
                        "existing_id": str(existing.id),
                    }
                )
                continue
            attendance = Attendance(
                attendance_date=row.attendance_date,
                attendance_taker_id=current_user.id,
                worker_name=row.worker_name,
                input_parts=row.input_parts,
                total_working_hours=row.total_working_hours,
                machine_stopped_time=row.machine_stopped_time,
                attendance_status=row.attendance_status,
                remarks=row.remarks,
                created_by=current_user.id,
            )
            db.add(attendance)
            db.flush()
            audit_service.record_created(db, attendance, changed_by=current_user.id)
            created.append(attendance)

    if errors:
        db.rollback()
        raise BulkValidationError(errors)

    db.commit()
    for attendance in created:
        db.refresh(attendance)
    return created
