from app.database import SessionLocal
from app.models.user import User, UserRole
from app.core.security import hash_password

def seed_admin():
    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.role == UserRole.ADMIN).first()
        if existing:
            print(f"Admin already exists: {existing.username}")
            return

        username = input("Admin username: ").strip()
        first_name = input("First name: ").strip()
        last_name = input("Last name: ").strip()
        email = input("Email: ").strip()
        password = input("Password (upper+lower+digit, 10+ chars): ").strip()

        admin = User(
            username=username,
            first_name=first_name,
            last_name=last_name,
            email=email,
            hashed_password=hash_password(password),
            role=UserRole.ADMIN,
            is_active=True,
        )
        db.add(admin)
        db.commit()
        print(f"Created admin '{username}'.")
    finally:
        db.close()

if __name__ == "__main__":
    seed_admin()