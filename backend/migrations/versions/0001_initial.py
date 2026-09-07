"""initial schema: users, attendance, audit_logs

Revision ID: 0001
Revises:
Create Date: 2026-09-06

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# create_type=False: type creation/drop is handled explicitly in upgrade()/downgrade()
# below (checkfirst=True) - without this, SQLAlchemy ALSO tries to create the type
# as part of create_table()'s own DDL, causing a duplicate-type error.
user_role = postgresql.ENUM("ADMIN", "SUPERVISOR", name="user_role", create_type=False)
user_status = postgresql.ENUM("ACTIVE", "INACTIVE", name="user_status", create_type=False)
attendance_status = postgresql.ENUM(
    "PRESENT", "ABSENT", "HALF_DAY", "LEAVE", name="attendance_status", create_type=False
)
audit_action = postgresql.ENUM("CREATED", "UPDATED", "DELETED", name="audit_action", create_type=False)


def upgrade() -> None:
    bind = op.get_bind()
    user_role.create(bind, checkfirst=True)
    user_status.create(bind, checkfirst=True)
    attendance_status.create(bind, checkfirst=True)
    audit_action.create(bind, checkfirst=True)

    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(150), nullable=False),
        sa.Column("email", sa.String(255), nullable=False, unique=True),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("role", user_role, nullable=False),
        sa.Column("phone", sa.String(30), nullable=True),
        sa.Column("department", sa.String(150), nullable=True),
        sa.Column("status", user_status, nullable=False, server_default="ACTIVE"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_users_email", "users", ["email"])

    op.create_table(
        "attendance",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("attendance_date", sa.Date, nullable=False),
        sa.Column(
            "attendance_taker_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id"),
            nullable=False,
        ),
        sa.Column("worker_name", sa.String(150), nullable=False),
        sa.Column("input_parts", sa.Numeric(10, 2), nullable=False, server_default="0"),
        sa.Column("total_working_hours", sa.Numeric(5, 2), nullable=False, server_default="0"),
        sa.Column("machine_stopped_time", sa.Numeric(5, 2), nullable=False, server_default="0"),
        sa.Column("attendance_status", attendance_status, nullable=False),
        sa.Column("remarks", sa.Text, nullable=True),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("updated_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("deleted_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("deletion_reason", sa.Text, nullable=True),
    )
    op.create_index("ix_attendance_date", "attendance", ["attendance_date"])
    op.create_index("ix_attendance_taker", "attendance", ["attendance_taker_id"])
    op.create_index("ix_attendance_status", "attendance", ["attendance_status"])
    op.create_index("ix_attendance_worker_name", "attendance", ["worker_name"])
    op.create_index("ix_attendance_created_at", "attendance", ["created_at"])
    op.create_index(
        "uq_attendance_date_worker_active",
        "attendance",
        ["attendance_date", "worker_name"],
        unique=True,
        postgresql_where=sa.text("deleted_at IS NULL"),
    )

    op.create_table(
        "audit_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "attendance_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("attendance.id"), nullable=False
        ),
        sa.Column("action", audit_action, nullable=False),
        sa.Column("old_data", postgresql.JSONB, nullable=True),
        sa.Column("new_data", postgresql.JSONB, nullable=True),
        sa.Column("changed_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("changed_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_audit_logs_attendance_id", "audit_logs", ["attendance_id"])


def downgrade() -> None:
    op.drop_table("audit_logs")
    op.drop_table("attendance")
    op.drop_table("users")
    audit_action.drop(op.get_bind(), checkfirst=True)
    attendance_status.drop(op.get_bind(), checkfirst=True)
    user_status.drop(op.get_bind(), checkfirst=True)
    user_role.drop(op.get_bind(), checkfirst=True)
