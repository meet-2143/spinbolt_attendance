"""Development-only seed data: 1 admin, 2 supervisors, sample attendance.

Run with: python -m app.seed
Credentials printed below are for local development ONLY - never reuse in production.
"""
import random
from datetime import date, timedelta

from app.auth.security import hash_password
from app.database.session import SessionLocal
from app.models.attendance import Attendance, AttendanceStatus
from app.models.user import User, UserRole, UserStatus

DEV_PASSWORD = "DevPass123!"

WORKERS = ["Amit Shah", "Raj Patel", "Jay Mehta", "Priya Sharma", "Vikram Singh"]


def seed() -> None:
    db = SessionLocal()
    try:
        if db.query(User).count() > 0:
            print("Seed data already present - skipping.")
            return

        admin = User(
            name="Admin User",
            email="admin@attendance.dev",
            password_hash=hash_password(DEV_PASSWORD),
            role=UserRole.ADMIN,
            status=UserStatus.ACTIVE,
        )
        supervisor1 = User(
            name="Rahul Patel",
            email="rahul.supervisor@attendance.dev",
            password_hash=hash_password(DEV_PASSWORD),
            role=UserRole.SUPERVISOR,
            department="Assembly Line A",
            status=UserStatus.ACTIVE,
        )
        supervisor2 = User(
            name="Sneha Desai",
            email="sneha.supervisor@attendance.dev",
            password_hash=hash_password(DEV_PASSWORD),
            role=UserRole.SUPERVISOR,
            department="Assembly Line B",
            status=UserStatus.ACTIVE,
        )
        db.add_all([admin, supervisor1, supervisor2])
        db.flush()

        today = date.today()
        for days_ago in range(5):
            day = today - timedelta(days=days_ago)
            for supervisor in (supervisor1, supervisor2):
                for worker in WORKERS:
                    status = random.choices(
                        [AttendanceStatus.PRESENT, AttendanceStatus.ABSENT, AttendanceStatus.HALF_DAY],
                        weights=[0.8, 0.1, 0.1],
                    )[0]
                    if status == AttendanceStatus.ABSENT:
                        parts, hours, stop = 0, 0, 0
                    else:
                        hours = 8 if status == AttendanceStatus.PRESENT else 4
                        stop = round(random.uniform(0, 1.5), 2)
                        parts = random.randint(300, 500)
                    db.add(
                        Attendance(
                            attendance_date=day,
                            attendance_taker_id=supervisor.id,
                            worker_name=f"{worker} ({supervisor.department})",
                            input_parts=parts,
                            total_working_hours=hours,
                            machine_stopped_time=stop,
                            attendance_status=status,
                            created_by=supervisor.id,
                        )
                    )

        db.commit()
        print("Seed complete. Dev accounts (password for all: %s):" % DEV_PASSWORD)
        print(f"  Admin:       {admin.email}")
        print(f"  Supervisor:  {supervisor1.email}")
        print(f"  Supervisor:  {supervisor2.email}")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
