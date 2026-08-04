from sqlalchemy.orm import Session
from models.user import User
from schemas.user import UserCreate, UserUpdate

class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_email(self, email: str):
        return self.db.query(User).filter(User.email == email).first()

    def get_by_id(self, user_id: int):
        return self.db.query(User).filter(User.user_id == user_id).first()

    # ADD THIS NEW METHOD HERE:
    def get_all(self):
        return self.db.query(User).all()


    def create(self, obj_in: UserCreate, hashed_password: str) -> User:
        db_user = User(
            username=obj_in.username,
            first_name=obj_in.first_name,
            last_name=obj_in.last_name,
            email=obj_in.email,
            role=obj_in.role,
            hashed_password=hashed_password
        )
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user

    def update(self, db_user: User, schema_data: UserUpdate) -> User:
        update_data = schema_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_user, key, value)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user

    def delete(self, db_user: User) -> User:
        self.db.delete(db_user)
        self.db.commit()
        return db_user
