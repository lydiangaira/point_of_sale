# Save as: routers/auth.py
from fastapi import APIRouter, Depends, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.config import settings
from app.database import get_db
from app.dependency import get_current_user
from app.models.user import User
from app.rate_limit import limiter
from app.schemas.auth import PasswordChange, RefreshRequest, Token
from app.schemas.user import UserRead
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/login", response_model=Token)
@limiter.limit(settings.login_rate_limit)
def login(request: Request, form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    return auth_service.login(db, form_data.username, form_data.password)

@router.post("/refresh", response_model=Token)
@limiter.limit(settings.default_rate_limit)
def refresh(request: Request, body: RefreshRequest, db: Session = Depends(get_db)):
    return auth_service.refresh(db, body.refresh_token)

@router.get("/me", response_model=UserRead)
def me(current_user: User = Depends(get_current_user)):
    return current_user

@router.post("/change-password", status_code=204)
def change_password(
    body: PasswordChange,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    auth_service.change_password(db, current_user, body.current_password, body.new_password)