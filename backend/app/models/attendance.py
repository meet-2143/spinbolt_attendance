import enum
import uuid
from datetime import date, datetime

from sqlalchemy import (
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy import Date as SQLDate
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.session import Base


class AttendanceStatus(str, enum.Enum):
    PRESENT = "PRESENT"
    ABSENT = "ABSENT"
    HALF_DAY = "HALF_DAY"
    LEAVE = "LEAVE"


class Attendance(Base):
    __tablename__ = "attendance"
    __table_args__ = (
        # Prevents duplicate attendance for the same worker on the same date.
        # Partial (WHERE deleted_at IS NULL) so a voided record frees up the slot.
        Index(
            "uq_attendance_date_worker_active",
            "attendance_date",
            "worker_name",
            unique=True,
            postgresql_where="deleted_at IS NULL",
        ),
        Index("ix_attendance_date", "attendance_date"),
        Index("ix_attendance_taker", "attendance_taker_id"),
        Index("ix_attendance_status", "attendance_status"),
        Index("ix_attendance_worker_name", "worker_name"),
        Index("ix_attendance_created_at", "created_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    attendance_date: Mapped[date] = mapped_column(SQLDate, nullable=False)
    attendance_taker_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    worker_name: Mapped[str] = mapped_column(String(150), nullable=False)
    input_parts: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False, default=0)
    total_working_hours: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False, default=0)
    machine_stopped_time: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False, default=0)
    attendance_status: Mapped[AttendanceStatus] = mapped_column(
        Enum(AttendanceStatus, name="attendance_status"), nullable=False
    )
    remarks: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    updated_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    deleted_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    deletion_reason: Mapped[str | None] = mapped_column(Text, nullable=True)

    attendance_taker: Mapped["User"] = relationship(  # noqa: F821
        "User", foreign_keys=[attendance_taker_id]
    )
