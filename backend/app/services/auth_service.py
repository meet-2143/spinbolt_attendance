from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.auth.security import verify_password
from app.models.user import User, UserStatus
from app.repositories import user_repository


def authenticate(db: Session, *, email: str, password: str) -> User:
    user = user_repository.get_by_email(db, email)
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password.")

    if user.status != UserStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This account has been deactivated. Contact an administrator.",
        )

    return user
