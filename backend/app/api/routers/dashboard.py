from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth.dependencies import require_admin, require_supervisor
from app.database.session import get_db
from app.models.user import User
from app.schemas.dashboard import AdminDashboardOut, SupervisorDashboardOut
from app.services import dashboard_service

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/supervisor", response_model=SupervisorDashboardOut)
def supervisor_dashboard(
    current_user: User = Depends(require_supervisor), db: Session = Depends(get_db)
) -> SupervisorDashboardOut:
    return dashboard_service.get_supervisor_dashboard(db, supervisor=current_user)


@router.get("/admin", response_model=AdminDashboardOut)
def admin_dashboard(
    date_from: date | None = None,
    date_to: date | None = None,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> AdminDashboardOut:
    return dashboard_service.get_admin_dashboard(db, date_from=date_from, date_to=date_to)
