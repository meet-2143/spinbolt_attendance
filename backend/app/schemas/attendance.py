import uuid
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, Field, model_validator

from app.models.attendance import AttendanceStatus


class AttendanceBase(BaseModel):
    attendance_date: date
    worker_name: str = Field(min_length=1, max_length=150)
    input_parts: Decimal = Field(ge=0, default=Decimal("0"), max_digits=10, decimal_places=2)
    total_working_hours: Decimal = Field(ge=0, default=Decimal("0"), max_digits=5, decimal_places=2)
    machine_stopped_time: Decimal = Field(ge=0, default=Decimal("0"), max_digits=5, decimal_places=2)
    attendance_status: AttendanceStatus
    remarks: str | None = Field(default=None, max_length=2000)

    @model_validator(mode="after")
    def apply_business_rules(self) -> "AttendanceBase":
        if self.attendance_status == AttendanceStatus.ABSENT:
            self.input_parts = Decimal("0")
            self.total_working_hours = Decimal("0")
            self.machine_stopped_time = Decimal("0")
        elif self.machine_stopped_time > self.total_working_hours:
            raise ValueError("Machine stopped time cannot exceed total working hours.")
        return self


class AttendanceCreate(AttendanceBase):
    pass


class AttendanceUpdate(AttendanceBase):
    pass


class AttendanceOut(BaseModel):
    id: uuid.UUID
    attendance_date: date
    attendance_taker_id: uuid.UUID
    attendance_taker_name: str
    worker_name: str
    input_parts: Decimal
    total_working_hours: Decimal
    machine_stopped_time: Decimal
    attendance_status: AttendanceStatus
    remarks: str | None
    created_at: datetime
    updated_at: datetime
    created_by: uuid.UUID
    updated_by: uuid.UUID | None


class BulkAttendanceRow(AttendanceBase):
    pass


class BulkAttendanceCreate(BaseModel):
    rows: list[BulkAttendanceRow] = Field(min_length=1, max_length=200)


class BulkRowError(BaseModel):
    row: int
    worker_name: str
    message: str
    existing_id: uuid.UUID | None = None


class VoidAttendanceRequest(BaseModel):
    reason: str = Field(min_length=1, max_length=500)
