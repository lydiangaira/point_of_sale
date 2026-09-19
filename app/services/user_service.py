from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.user import User, UserRole
from app.repositories.user_repository import user_repository
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import hash_password

def create_user(db: Session, data: UserCreate) -> User:
    if user_repository.get_by_username(db, data.username):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already exists")
    if user_repository.get_by_email(db, data.email):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already exists")

    values = data.model_dump(exclude={"password"})
    values["hashed_password"] = hash_password(data.password)
    return user_repository.create(db, values)

def get_user(db: Session, user_id: UUID) -> User:
    user = user_repository.get_by_id(db, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user

def update_user(db: Session, user_id: UUID, data: UserUpdate, current_user: User) -> User:
    user = get_user(db, user_id)

    values = data.model_dump(exclude_unset=True)
    if current_user.role != UserRole.ADMIN:
        if user.user_id != current_user.user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
        values.pop("role", None)
        values.pop("is_active", None)

    if "email" in values and values["email"] != user.email and user_repository.get_by_email(db, values["email"]):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already exists")

    return user_repository.update(db, user, values)

def deactivate_user(db: Session, user_id: UUID, current_user: User) -> User:
    if user_id == current_user.user_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot deactivate your own account")
    user = get_user(db, user_id)
    return user_repository.update(db, user, {"is_active": False})