import uuid
from datetime import datetime, timedelta, timezone
from typing import Literal

import jwt
from pwdlib import PasswordHash

from app.core.config import settings

password_hash = PasswordHash.recommended()

def hash_password(password: str) -> str:
    return password_hash.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_hash.verify(plain_password, hashed_password)

def _create_token(subject: str, expires_delta: timedelta, token_type: Literal["access", "refresh"]) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": subject,
        "type": token_type,
        "iat": now,
        "exp": now + expires_delta,
        "jti": str(uuid.uuid4()),  # unique id, needed if you add a revocation/blacklist later
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)

def create_access_token(user_id: str) -> str:
    return _create_token(user_id, timedelta(minutes=settings.access_token_expire_minutes), "access")

def create_refresh_token(user_id: str) -> str:
    return _create_token(user_id, timedelta(days=settings.refresh_token_expire_days), "refresh")

def decode_token(token: str, expected_type: Literal["access", "refresh"] = "access") -> dict:
    payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
    if payload.get("type") != expected_type:
        raise jwt.InvalidTokenError("Unexpected token type")
    return payload