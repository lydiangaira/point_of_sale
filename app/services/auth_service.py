import jwt
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.repositories.user_repository import user_repository
from app.core.security import create_access_token, create_refresh_token, decode_token, hash_password, verify_password

_DUMMY_HASH = hash_password("not-a-real-password-x7#Q")

_bad_credentials = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Incorrect username or password",
    headers={"WWW-Authenticate": "Bearer"},
)

def login(db: Session, username: str, password: str) -> dict:
    user = user_repository.get_by_username(db, username)
    if user is None:
        verify_password(password, _DUMMY_HASH)
        raise _bad_credentials
    if not verify_password(password, user.hashed_password):
        raise _bad_credentials
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is inactive")

    uid = str(user.user_id)
    return {
        "access_token": create_access_token(uid),
        "refresh_token": create_refresh_token(uid),
        "token_type": "bearer",
    }

def refresh(db: Session, refresh_token: str) -> dict:
    invalid = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired refresh token")
    try:
        payload = decode_token(refresh_token, expected_type="refresh")
        user_id = payload["sub"]
    except (jwt.InvalidTokenError, KeyError):
        raise invalid

    user = user_repository.get_by_id(db, user_id)
    if user is None or not user.is_active:
        raise invalid

    uid = str(user.user_id)
    return {
        "access_token": create_access_token(uid),
        "refresh_token": create_refresh_token(uid),
        "token_type": "bearer",
    }

def change_password(db: Session, user, current_password: str, new_password: str) -> None:
    if not verify_password(current_password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Current password is incorrect")
    user_repository.update(db, user, {"hashed_password": hash_password(new_password)})