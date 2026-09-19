from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate

class UserRepository:
    def get_by_username(self, db: Session, username: str):
        return db.query(User).filter(User.username == username).first()

    def get_by_email(self, db: Session, email: str):
        return db.query(User).filter(User.email == email).first()

    def get_by_id(self, db: Session, user_id: int):
        return db.query(User).filter(User.user_id == user_id).first()

    def get_all(self, db: Session):
        return db.query(User).all()

    def create(self, db: Session, obj_in: UserCreate, hashed_password: str) -> User:
        db_user = User(
            username=obj_in.username,
            first_name=obj_in.first_name,
            last_name=obj_in.last_name,
            email=obj_in.email,
            role=obj_in.role,
            hashed_password=hashed_password,
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

    def update(self, db: Session, db_user: User, schema_data: UserUpdate) -> User:
        update_data = schema_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_user, key, value)
        db.commit()
        db.refresh(db_user)
        return db_user

    def delete(self, db: Session, db_user: User) -> User:
        db.delete(db_user)
        db.commit()
        return db_user

user_repository = UserRepository()