from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from sqlalchemy.orm import Session
import os
from dotenv import load_dotenv

from app.database.database import get_db
from app.models.users import User
from app.utils.permissions import Role
from app.logger import logger

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"

security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    token = credentials.credentials
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials."
    )

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )
        email = payload.get("sub")

        if email is None:
            raise credentials_exception

    except JWTError:
        raise credentials_exception

    user = (
        db.query(User)
        .filter(User.email == email)
        .first()
    )

    if user is None:
        raise credentials_exception

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive."
        )

    return user


def require_roles(*allowed: Role):
    """Build a dependency that only lets the given roles through."""

    allowed_values = [role.value for role in allowed]

    def checker(
        current_user: User = Depends(get_current_user)
    ) -> User:
        if current_user.role not in allowed_values:
            logger.warning(
                "ACCESS DENIED - user=%s role=%s requires=%s",
                current_user.email,
                current_user.role,
                allowed_values,
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    f"Access denied. Requires one of {allowed_values}; "
                    f"your role is '{current_user.role}'."
                ),
            )

        logger.info(
            "ACCESS GRANTED - user=%s role=%s",
            current_user.email,
            current_user.role,
        )
        return current_user

    return checker


require_admin = require_roles(Role.ADMIN)

require_uploader = require_roles(Role.ADMIN, Role.ANALYST)

require_any = require_roles(Role.ADMIN, Role.ANALYST, Role.REVIEWER)
