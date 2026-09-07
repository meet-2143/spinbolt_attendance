from datetime import date, datetime, timedelta

from sqlalchemy import case, func, select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models.attendance import Attendance, AttendanceStatus
from app.models.user import User
from app.schemas.dashboard import AdminDashboardOut, SupervisorDashboardOut, SupervisorSummaryRow, TrendPoint
from app.services.attendance_service import build_attendance_out

settings = get_settings()


def _today() -> date:
    return datetime.now(settings.tzinfo).date()


def get_supervisor_dashboard(db: Session, *, supervisor: User) -> SupervisorDashboardOut:
    today = _today()

    agg_stmt = select(
        func.count().label("total"),
        func.coalesce(func.sum(case((Attendance.attendance_status == AttendanceStatus.PRESENT, 1), else_=0)), 0).label(
            "present"
        ),
        func.coalesce(func.sum(case((Attendance.attendance_status == AttendanceStatus.ABSENT, 1), else_=0)), 0).label(
            "absent"
        ),
        func.coalesce(func.sum(Attendance.total_working_hours), 0).label("total_hours"),
        func.coalesce(func.sum(Attendance.machine_stopped_time), 0).label("total_stop"),
        func.coalesce(func.sum(Attendance.input_parts), 0).label("total_parts"),
    ).where(
        Attendance.attendance_taker_id == supervisor.id,
        Attendance.attendance_date == today,
        Attendance.deleted_at.is_(None),
    )
    row = db.execute(agg_stmt).one()

    recent_stmt = (
        select(Attendance)
        .join(User, Attendance.attendance_taker_id == User.id)
        .where(Attendance.attendance_taker_id == supervisor.id, Attendance.deleted_at.is_(None))
        .order_by(Attendance.created_at.desc())
        .limit(10)
    )
    recent = list(db.scalars(recent_stmt))

    return SupervisorDashboardOut(
        today_count=row.total,
        present_count=row.present,
        absent_count=row.absent,
        total_working_hours=row.total_hours,
        total_machine_stopped_time=row.total_stop,
        total_input_parts=row.total_parts,
        recent_entries=[build_attendance_out(a) for a in recent],
    )


def get_admin_dashboard(db: Session, *, date_from: date | None = None, date_to: date | None = None) -> AdminDashboardOut:
    today = _today()
    trend_from = date_from or (today - timedelta(days=13))
    trend_to = date_to or today

    total_records = db.scalar(
        select(func.count()).select_from(Attendance).where(Attendance.deleted_at.is_(None))
    ) or 0

    today_stmt = select(
        func.count().label("total"),
        func.coalesce(func.sum(case((Attendance.attendance_status == AttendanceStatus.PRESENT, 1), else_=0)), 0).label(
            "present"
        ),
        func.coalesce(func.sum(case((Attendance.attendance_status == AttendanceStatus.ABSENT, 1), else_=0)), 0).label(
            "absent"
        ),
    ).where(Attendance.attendance_date == today, Attendance.deleted_at.is_(None))
    today_row = db.execute(today_stmt).one()

    totals_stmt = select(
        func.coalesce(func.sum(Attendance.total_working_hours), 0).label("total_hours"),
        func.coalesce(func.sum(Attendance.machine_stopped_time), 0).label("total_stop"),
        func.coalesce(func.sum(Attendance.input_parts), 0).label("total_parts"),
    ).where(Attendance.deleted_at.is_(None))
    totals_row = db.execute(totals_stmt).one()

    trend_stmt = (
        select(
            Attendance.attendance_date.label("period"),
            func.count().label("total"),
            func.coalesce(
                func.sum(case((Attendance.attendance_status == AttendanceStatus.PRESENT, 1), else_=0)), 0
            ).label("present"),
            func.coalesce(
                func.sum(case((Attendance.attendance_status == AttendanceStatus.ABSENT, 1), else_=0)), 0
            ).label("absent"),
        )
        .where(
            Attendance.deleted_at.is_(None),
            Attendance.attendance_date >= trend_from,
            Attendance.attendance_date <= trend_to,
        )
        .group_by(Attendance.attendance_date)
        .order_by(Attendance.attendance_date)
    )
    trend = [TrendPoint(period=r.period, total=r.total, present=r.present, absent=r.absent) for r in db.execute(trend_stmt)]

    supervisor_stmt = (
        select(
            User.id.label("supervisor_id"),
            User.name.label("supervisor_name"),
            func.count(Attendance.id).label("entries"),
            func.coalesce(func.sum(Attendance.total_working_hours), 0).label("total_hours"),
            func.coalesce(func.sum(Attendance.machine_stopped_time), 0).label("total_stop"),
            func.coalesce(func.sum(Attendance.input_parts), 0).label("total_parts"),
        )
        .join(Attendance, Attendance.attendance_taker_id == User.id)
        .where(
            Attendance.deleted_at.is_(None),
            Attendance.attendance_date >= trend_from,
            Attendance.attendance_date <= trend_to,
        )
        .group_by(User.id, User.name)
        .order_by(User.name)
    )
    supervisor_summary = [
        SupervisorSummaryRow(
            supervisor_id=r.supervisor_id,
            supervisor_name=r.supervisor_name,
            entries=r.entries,
            total_working_hours=r.total_hours,
            total_machine_stopped_time=r.total_stop,
            total_input_parts=r.total_parts,
        )
        for r in db.execute(supervisor_stmt)
    ]

    return AdminDashboardOut(
        total_attendance_records=total_records,
        today_count=today_row.total,
        present_today=today_row.present,
        absent_today=today_row.absent,
        total_working_hours=totals_row.total_hours,
        total_machine_stopped_time=totals_row.total_stop,
        total_input_parts=totals_row.total_parts,
        trend=trend,
        supervisor_summary=supervisor_summary,
    )
