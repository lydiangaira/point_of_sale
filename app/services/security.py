from datetime import datetime, timedelta, timezone
from typing import Any, Union
from jose import jwt
from pwdlib import PasswordHash
from core.config import settings

password_hash = PasswordHash.recommended()

def get_password_hash(password: str) -> str:
    """
    Transforms raw user credentials into a one-way secure cryptographic string.
    Automatically generates a unique salt string behind the scenes.
    """
    return password_hash.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Validates an incoming plain text password string matches the stored, 
    salted Argon2id hash sequence from the database.
    """
    return password_hash.verify(plain_password, hashed_password)


def create_access_token(subject: Union[str, Any], expires_delta: timedelta = None) -> str:
    """
    Mints a secure, tamper-proof JWT token signed via HS256.
    The front-end fronting client must send this token with every future request.
    """
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        # Defaults to the shift duration configured in settings (e.g., 8 hours)
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # Store the user's UUID string safely inside the token's subject field
    to_encode = {
        "exp": expire, 
        "sub": str(subject)
    }
    
    # Signs and seals the payload with your secure secret key using HS256
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt
