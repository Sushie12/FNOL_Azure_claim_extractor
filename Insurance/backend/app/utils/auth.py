
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from sqlalchemy.orm import Session
import os
from dotenv import load_dotenv

from app.database.database import get_db
from app.models.users import User

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

    return user

def require_admin(
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "Admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required.",
        )

    return current_user



# from fastapi import Depends, HTTPException, status
# from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
# from jose import JWTError, jwt
# from sqlalchemy.orm import Session
# import os
# from dotenv import load_dotenv

# from app.database.database import get_db
# from app.models.users import User

# load_dotenv()

# SECRET_KEY = os.getenv("SECRET_KEY")
# ALGORITHM = "HS256"

# security = HTTPBearer()

# def get_current_user(
# credentials: HTTPAuthorizationCredentials = Depends(security),
# db: Session = Depends(get_db)
# ):
# token = credentials.credentials

# ```
# credentials_exception = HTTPException(
#     status_code=status.HTTP_401_UNAUTHORIZED,
#     detail="Could not validate credentials.",
# )

# try:
#     payload = jwt.decode(
#         token,
#         SECRET_KEY,
#         algorithms=[ALGORITHM]
#     )

#     email = payload.get("sub")

#     if email is None:
#         raise credentials_exception

# except JWTError:
#     raise credentials_exception

# user = (
#     db.query(User)
#     .filter(User.email == email)
#     .first()
# )

# if user is None:
#     raise credentials_exception

# return user
# ```
