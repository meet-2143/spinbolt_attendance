import uuid
from datetime import datetime

from pydantic import BaseModel

from app.models.audit_log import AuditAction


class AuditLogOut(BaseModel):
    id: uuid.UUID
    attendance_id: uuid.UUID
    action: AuditAction
    old_data: dict | None
    new_data: dict | None
    changed_by: uuid.UUID
    changed_by_name: str
    changed_at: datetime
