import uuid
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.auth.dependencies import require_admin, require_any_role
from app.database.session import get_db
from app.models.attendance import AttendanceStatus
from app.models.user import User, UserRole
from app.repositories import attendance_repository
from app.repositories.attendance_repository import AttendanceFilters
from app.schemas.attendance import (
    AttendanceCreate,
    AttendanceOut,
    AttendanceUpdate,
    BulkAttendanceCreate,
    VoidAttendanceRequest,
)
from app.schemas.common import PagedResponse
from app.services import attendance_service, export_service
from app.services.exceptions import BulkValidationError, DuplicateAttendanceError

router = APIRouter(prefix="/api/attendance", tags=["attendance"])


def _duplicate_response(exc: DuplicateAttendanceError) -> HTTPException:
    return HTTPException(
        status_code=409,
        detail={
            "message": "Attendance already exists for this worker on this date.",
            "existing_id": str(exc.existing_id),
        },
    )


@router.get("", response_model=PagedResponse[AttendanceOut])
def list_attendance(
    date_from: date | None = None,
    date_to: date | None = None,
    status: AttendanceStatus | None = None,
    search: str | None = None,
    supervisor_id: uuid.UUID | None = None,
    sort_by: str = "attendance_date",
    sort_dir: str = "desc",
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(require_any_role),
    db: Session = Depends(get_db),
) -> PagedResponse[AttendanceOut]:
    # A supervisor is always hard-scoped to their own records server-side -
    # never trust a client-supplied supervisor id for this. Admins may
    # optionally filter by a specific supervisor.
    if current_user.role == UserRole.SUPERVISOR:
        taker_id = current_user.id
    else:
        taker_id = supervisor_id

    filters = AttendanceFilters(
        taker_id=taker_id,
        date_from=date_from,
        date_to=date_to,
        status=status,
        search=search,
        sort_by=sort_by,
        sort_dir=sort_dir,
        page=page,
        page_size=page_size,
    )
    items, total = attendance_repository.list_paginated(db, filters)
    return PagedResponse(
        items=[attendance_service.build_attendance_out(a) for a in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/worker-names", response_model=list[str])
def worker_names(
    q: str | None = None, current_user: User = Depends(require_any_role), db: Session = Depends(get_db)
) -> list[str]:
    return attendance_repository.distinct_worker_names(db, q)


@router.get("/export")
def export_attendance(
    export_format: str = Query("csv", alias="format", pattern="^(csv|excel|pdf)$"),
    date_from: date | None = None,
    date_to: date | None = None,
    status: AttendanceStatus | None = None,
    search: str | None = None,
    supervisor_id: uuid.UUID | None = None,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> Response:
    # Exports reuse the exact same filtered query as the on-screen table/report,
    # so the downloaded file always matches what the admin was looking at.
    filters = AttendanceFilters(
        taker_id=supervisor_id, date_from=date_from, date_to=date_to, status=status, search=search
    )
    records = attendance_repository.list_all(db, filters)

    generators = {
        "csv": (export_service.to_csv, "text/csv", "csv"),
        "excel": (
            export_service.to_excel,
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "xlsx",
        ),
        "pdf": (export_service.to_pdf, "application/pdf", "pdf"),
    }
    generate, media_type, extension = generators[export_format]

    return Response(
        content=generate(records),
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="attendance-export.{extension}"'},
    )


@router.post("", response_model=AttendanceOut, status_code=201)
def create_attendance(
    payload: AttendanceCreate, current_user: User = Depends(require_any_role), db: Session = Depends(get_db)
) -> AttendanceOut:
    try:
        attendance = attendance_service.create_attendance(db, payload=payload, current_user=current_user)
    except DuplicateAttendanceError as exc:
        raise _duplicate_response(exc) from exc
    return attendance_service.build_attendance_out(attendance)


@router.post("/bulk", response_model=list[AttendanceOut], status_code=201)
def bulk_create_attendance(
    payload: BulkAttendanceCreate,
    current_user: User = Depends(require_any_role),
    db: Session = Depends(get_db),
) -> list[AttendanceOut]:
    try:
        created = attendance_service.bulk_create_attendance(db, rows=payload.rows, current_user=current_user)
    except BulkValidationError as exc:
        raise HTTPException(
            status_code=422,
            detail={"message": "Some rows could not be saved. No records were created.", "errors": exc.errors},
        ) from exc
    return [attendance_service.build_attendance_out(a) for a in created]


@router.get("/{attendance_id}", response_model=AttendanceOut)
def get_attendance(
    attendance_id: uuid.UUID, current_user: User = Depends(require_any_role), db: Session = Depends(get_db)
) -> AttendanceOut:
    attendance = attendance_service.get_attendance_or_404(db, attendance_id, current_user=current_user)
    return attendance_service.build_attendance_out(attendance)


@router.put("/{attendance_id}", response_model=AttendanceOut)
def update_attendance(
    attendance_id: uuid.UUID,
    payload: AttendanceUpdate,
    current_user: User = Depends(require_any_role),
    db: Session = Depends(get_db),
) -> AttendanceOut:
    try:
        attendance = attendance_service.update_attendance(
            db, attendance_id=attendance_id, payload=payload, current_user=current_user
        )
    except DuplicateAttendanceError as exc:
        raise _duplicate_response(exc) from exc
    return attendance_service.build_attendance_out(attendance)


@router.delete("/{attendance_id}", status_code=200)
def void_attendance(
    attendance_id: uuid.UUID,
    payload: VoidAttendanceRequest,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> dict:
    attendance_service.void_attendance(
        db, attendance_id=attendance_id, reason=payload.reason, current_user=current_user
    )
    return {"success": True}
