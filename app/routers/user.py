from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependency import get_current_user, require_roles
from app.models.user import User, UserRole
from app.schemas.user import UserCreate, UserRead, UserUpdate
from app.services import user_service

router = APIRouter(prefix="/users", tags=["users"])

# No POST /users/register anywhere in this API. Account creation always
# goes through this admin-gated endpoint.
admin_only = require_roles(UserRole.ADMIN)

@router.post("", response_model=UserRead, status_code=201, dependencies=[Depends(admin_only)])
def create_user(data: UserCreate, db: Session = Depends(get_db)):
    return user_service.create_user(db, data)

@router.get("", response_model=list[UserRead], dependencies=[Depends(admin_only)])
def list_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    from repositories.user_repository import user_repository

    return user_repository.list(db, skip=skip, limit=limit)

@router.get("/{user_id}", response_model=UserRead, dependencies=[Depends(admin_only)])
def get_user(user_id: UUID, db: Session = Depends(get_db)):
    return user_service.get_user(db, user_id)

@router.patch("/{user_id}", response_model=UserRead)
def update_user(
    user_id: UUID,
    data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return user_service.update_user(db, user_id, data, current_user)

@router.delete("/{user_id}", status_code=204, dependencies=[Depends(admin_only)])
def deactivate_user(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    user_service.deactivate_user(db, user_id, current_user)