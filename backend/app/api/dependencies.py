from typing import Generator

from fastapi import Depends, HTTPException, status
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from app.core import security
from app.core.config import settings
from app.db.session import SessionLocal
from app import crud, models, schemas

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)

def get_db() -> Generator[Session, None, None]:
    """Provide a new SQLAlchemy session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(security.oauth2_scheme),
) -> models.User:
    """Retrieve the currently authenticated user from the JWT."""
    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[security.ALGORITHM],
        )
        user_id: int = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = crud.user.get(db, id=user_id)
    if not user:
        raise credentials_exception
    return user
