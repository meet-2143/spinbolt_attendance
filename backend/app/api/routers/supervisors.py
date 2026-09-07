import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth.dependencies import require_admin
from app.database.session import get_db
from app.models.user import User
from app.schemas.user import (
    SupervisorCreate,
    SupervisorPasswordReset,
    SupervisorStatusUpdate,
    SupervisorUpdate,
    UserOut,
)
from app.services import supervisor_service

router = APIRouter(prefix="/api/supervisors", tags=["supervisors"], dependencies=[Depends(require_admin)])


@router.get("", response_model=list[UserOut])
def list_supervisors(db: Session = Depends(get_db)) -> list[User]:
    return supervisor_service.list_supervisors(db)


@router.post("", response_model=UserOut, status_code=201)
def create_supervisor(payload: SupervisorCreate, db: Session = Depends(get_db)) -> User:
    return supervisor_service.create_supervisor(db, payload)


@router.get("/{supervisor_id}", response_model=UserOut)
def get_supervisor(supervisor_id: uuid.UUID, db: Session = Depends(get_db)) -> User:
    return supervisor_service.get_supervisor_or_404(db, supervisor_id)


@router.put("/{supervisor_id}", response_model=UserOut)
def update_supervisor(supervisor_id: uuid.UUID, payload: SupervisorUpdate, db: Session = Depends(get_db)) -> User:
    return supervisor_service.update_supervisor(db, supervisor_id, payload)


@router.patch("/{supervisor_id}/status", response_model=UserOut)
def update_supervisor_status(
    supervisor_id: uuid.UUID, payload: SupervisorStatusUpdate, db: Session = Depends(get_db)
) -> User:
    return supervisor_service.set_supervisor_status(db, supervisor_id, payload.status)


@router.patch("/{supervisor_id}/reset-password")
def reset_supervisor_password(
    supervisor_id: uuid.UUID, payload: SupervisorPasswordReset, db: Session = Depends(get_db)
) -> dict:
    supervisor_service.reset_supervisor_password(db, supervisor_id, payload.new_password)
    return {"success": True}
