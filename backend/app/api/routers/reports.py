from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.auth.dependencies import require_admin
from app.database.session import get_db
from app.schemas.attendance import AttendanceOut
from app.services import attendance_service, report_service

router = APIRouter(prefix="/api/reports", tags=["reports"], dependencies=[Depends(require_admin)])


@router.get("/daily", response_model=list[AttendanceOut])
def daily_report(report_date: date = Query(..., alias="date"), db: Session = Depends(get_db)) -> list[AttendanceOut]:
    records = report_service.daily_report(db, report_date=report_date)
    return [attendance_service.build_attendance_out(r) for r in records]


@router.get("/range", response_model=list[AttendanceOut])
def range_report(
    date_from: date = Query(...), date_to: date = Query(...), db: Session = Depends(get_db)
) -> list[AttendanceOut]:
    if date_from > date_to:
        raise HTTPException(status_code=422, detail="'date_from' must not be after 'date_to'.")
    records = report_service.generate_report(db, date_from=date_from, date_to=date_to)
    return [attendance_service.build_attendance_out(r) for r in records]


@router.get("/monthly", response_model=list[AttendanceOut])
def monthly_report(
    year: int = Query(..., ge=2000, le=2100), month: int = Query(..., ge=1, le=12), db: Session = Depends(get_db)
) -> list[AttendanceOut]:
    records = report_service.monthly_report(db, year=year, month=month)
    return [attendance_service.build_attendance_out(r) for r in records]
