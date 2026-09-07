import uuid
from datetime import date
from decimal import Decimal

from pydantic import BaseModel

from app.schemas.attendance import AttendanceOut


class SupervisorDashboardOut(BaseModel):
    today_count: int
    present_count: int
    absent_count: int
    total_working_hours: Decimal
    total_machine_stopped_time: Decimal
    total_input_parts: Decimal
    recent_entries: list[AttendanceOut]


class TrendPoint(BaseModel):
    period: date
    total: int
    present: int
    absent: int


class SupervisorSummaryRow(BaseModel):
    supervisor_id: uuid.UUID
    supervisor_name: str
    entries: int
    total_working_hours: Decimal
    total_machine_stopped_time: Decimal
    total_input_parts: Decimal


class AdminDashboardOut(BaseModel):
    total_attendance_records: int
    today_count: int
    present_today: int
    absent_today: int
    total_working_hours: Decimal
    total_machine_stopped_time: Decimal
    total_input_parts: Decimal
    trend: list[TrendPoint]
    supervisor_summary: list[SupervisorSummaryRow]
