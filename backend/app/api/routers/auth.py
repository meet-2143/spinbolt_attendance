from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.auth.security import ACCESS_TOKEN_COOKIE_NAME, create_access_token
from app.config import get_settings
from app.database.session import get_db
from app.models.user import User
from app.schemas.auth import LoginRequest, LoginResponse
from app.schemas.user import UserOut
from app.services import auth_service

router = APIRouter(prefix="/api/auth", tags=["auth"])
settings = get_settings()


def _set_auth_cookie(response: Response, token: str) -> None:
    response.set_cookie(
        key=ACCESS_TOKEN_COOKIE_NAME,
        value=token,
        httponly=True,
        secure=settings.environment != "development",
        samesite="lax",
        max_age=settings.jwt_expire_minutes * 60,
        path="/",
    )


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest, response: Response, db: Session = Depends(get_db)) -> LoginResponse:
    user = auth_service.authenticate(db, email=payload.email, password=payload.password)
    token = create_access_token(user_id=user.id, role=user.role.value)
    _set_auth_cookie(response, token)
    return LoginResponse(user=UserOut.model_validate(user))


@router.post("/logout")
def logout(response: Response) -> dict:
    response.delete_cookie(ACCESS_TOKEN_COOKIE_NAME, path="/")
    return {"success": True}


@router.get("/me", response_model=UserOut)
def me(current_user: User = Depends(get_current_user)) -> UserOut:
    return UserOut.model_validate(current_user)
