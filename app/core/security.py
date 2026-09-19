from datetime import timezone, timedelta, datetime

import jwt
from pwdlib import PasswordHash

from app.core.config import settings

password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_hash.verify(plain_password, hashed_password)


def create_access_token(user_id) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    payload = {"sub": str(user_id), "exp": expire, "type": "access"}
    return jwt.encode(payload, settings.jwt_private_key, algorithm=settings.jwt_access_algorithm)


def create_refresh_token(user_id) -> str:
    expire = datetime.now(timezone.utc) + timedelta(days=settings.refresh_token_expire_days)
    payload = {"sub": str(user_id), "exp": expire, "type": "refresh"}
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_refresh_algorithm)


def decode_token(token: str, expected_type: str = "access") -> dict:
    if expected_type == "access":
        payload = jwt.decode(token, settings.jwt_public_key, algorithms=[settings.jwt_access_algorithm])
    elif expected_type == "refresh":
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_refresh_algorithm])
    else:
        raise ValueError(f"Unknown token type: {expected_type}")

    if payload.get("type") != expected_type:
        raise jwt.InvalidTokenError("Token type mismatch")
    return payload