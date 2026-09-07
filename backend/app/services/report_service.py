import calendar
from datetime import date

from sqlalchemy.orm import Session

from app.models.attendance import Attendance
from app.repositories import attendance_repository
from app.repositories.attendance_repository import AttendanceFilters


def generate_report(db: Session, *, date_from: date, date_to: date) -> list[Attendance]:
    filters = AttendanceFilters(date_from=date_from, date_to=date_to, sort_by="attendance_date", sort_dir="asc")
    return attendance_repository.list_all(db, filters)


def daily_report(db: Session, *, report_date: date) -> list[Attendance]:
    return generate_report(db, date_from=report_date, date_to=report_date)


def monthly_report(db: Session, *, year: int, month: int) -> list[Attendance]:
    last_day = calendar.monthrange(year, month)[1]
    return generate_report(db, date_from=date(year, month, 1), date_to=date(year, month, last_day))
