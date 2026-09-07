import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field

from app.models.user import UserRole, UserStatus


class UserOut(BaseModel):
    id: uuid.UUID
    name: str
    email: EmailStr
    role: UserRole
    phone: str | None
    department: str | None
    status: UserStatus
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class SupervisorCreate(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    phone: str | None = Field(default=None, max_length=30)
    department: str | None = Field(default=None, max_length=150)


class SupervisorUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=150)
    phone: str | None = Field(default=None, max_length=30)
    department: str | None = Field(default=None, max_length=150)


class SupervisorStatusUpdate(BaseModel):
    status: UserStatus


class SupervisorPasswordReset(BaseModel):
    new_password: str = Field(min_length=8, max_length=128)
