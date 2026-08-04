from sqlalchemy.orm import Session
from uuid import UUID
from typing import List
from fastapi import HTTPException, status
from repositories.user_repository import UserRepository
from schemas.user import UserCreate, UserUpdate 
from models.user import User
from services.security import get_password_hash


class UserService:
    def __init__(self, db: Session):
        self.repo = UserRepository(db)

    def create_user(self, obj_in: UserCreate):
        if self.repo.get_by_email(obj_in.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered."
            )
        
        secure_hashed_password = get_password_hash(obj_in.password)
        return self.repo.create(obj_in, hashed_password=secure_hashed_password)

    def update_user(self, user_id: int, obj_in: UserUpdate):
        # 1. Fetch the existing user from the database
        db_user = self.repo.get_by_id(user_id)
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found."
            )
        
        # 2. Extract input data into a dictionary
        update_data = obj_in.model_dump(exclude_unset=True)
        
        # 3. INTERCEPT PASSWORD CHANGES: Hash it safely if provided
        if "password" in update_data and update_data["password"]:
            secure_hashed_password = get_password_hash(update_data["password"])
            update_data["hashed_password"] = secure_hashed_password
            del update_data["password"] # Remove plain text from data dict
            
        # 4. Pass the cleaned update dictionary to your repository
        return self.repo.update(db_user, update_data)

