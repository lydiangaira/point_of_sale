from typing import Generator
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from pydantic import ValidationError
from sqlalchemy.orm import Session
from uuid import UUID
from models.user import User, UserRole

# Example usage for your routes protection decorators:
# Depends(RoleChecker([UserRole.STORE_OWNER, UserRole.STORE_MANAGER]))


from database import session
from app.core.config import settings
from models.user import User, UserRole
from schemas.user import TokenData

# Maps auth token capture straight from the incoming standard Authorization request headers
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")

def get_db() -> Generator:
    """Yields clean isolated atomic transaction execution threads per request pipeline."""
    db = session()
    try:
        yield db
    finally:
        db.close()

def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)) -> User:
    """Interceptors to unpack, decrypt, and parse ongoing operational user profile contexts."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        token_data = TokenData(id=payload.get("sub"))
    except (JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication credentials could not be successfully validated.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = db.query(User).filter(User.user_id == UUID(token_data.id)).first()
    if not user:
        raise HTTPException(status_code=404, detail="Active worker account could not be found.")
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Worker account is flagged as inactive.")
    return user

class RoleChecker:
    """Guard parameters checking system roles access compliance flags."""
    def __init__(self, allowed_roles: list[UserRole]):
        self.allowed_roles = allowed_roles

    def __call__(self, current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in [role.value for role in self.allowed_roles]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Your account lacks the clear operational security clearance to view this node."
            )
        return current_user
