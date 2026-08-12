from sqlalchemy.orm import Session

from app.database.database import SessionLocal
from app.models.users import User
from app.utils.permissions import Role
from app.utils.security import hash_password


DEFAULT_USERS = [
    {
        "full_name": "System Administrator",
        "email": "admin@insurance.com",
        "password": "Admin@123",
        "role": Role.ADMIN.value,
    },
    {
        "full_name": "Claims Analyst",
        "email": "analyst@insurance.com",
        "password": "Analyst@123",
        "role": Role.ANALYST.value,
    },
    {
        "full_name": "Claims Reviewer",
        "email": "reviewer@insurance.com",
        "password": "Reviewer@123",
        "role": Role.REVIEWER.value,
    },
]


def seed_users():
    db: Session = SessionLocal()

    try:
        for entry in DEFAULT_USERS:
            existing_user = (
                db.query(User)
                .filter(User.email == entry["email"])
                .first()
            )

            if existing_user:
                print(f"{entry['email']} already exists. Skipping.")
                continue

            user = User(
                full_name=entry["full_name"],
                email=entry["email"],
                password_hash=hash_password(entry["password"]),
                role=entry["role"],
                is_active=True,
            )

            db.add(user)
            print(f"Created {entry['email']} with role {entry['role']}.")

        db.commit()

    finally:
        db.close()


if __name__ == "__main__":
    seed_users()
