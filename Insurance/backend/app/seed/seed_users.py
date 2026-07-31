from sqlalchemy.orm import Session

from app.database.database import SessionLocal
from app.models.users import User
from app.utils.security import hash_password


def seed_admin():
    db: Session = SessionLocal()

    try:
        existing_user = (
            db.query(User)
            .filter(User.email == "admin@insurance.com")
            .first()
        )

        if existing_user:
            print("Admin user already exists.")
            return

        admin = User(
            full_name="System Administrator",
            email="admin@insurance.com",
            password_hash=hash_password("Admin@123"),
            role="Admin",
            is_active=True
        )

        db.add(admin)
        db.commit()

        print("Admin user created successfully.")

    finally:
        db.close()


if __name__ == "__main__":
    seed_admin()