from typing import AsyncGenerator

from fastapi import Depends, HTTPException, status
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import security
from app.core.config import settings
from app.core.rate_limiter import RateLimiters
from app.db.models.user import User as UserModel
from app.containers import container

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Provide a new SQLAlchemy session."""
    async for session in container.db():
        yield session

async def get_current_user(
    db: AsyncSession = Depends(get_db),
    token: str = Depends(security.oauth2_scheme),
) -> UserModel:
    """Retrieve the currently authenticated user from the JWT."""
    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm],
        )
        user_id: int = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = await db.get(UserModel, user_id)
    if not user:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: UserModel = Depends(get_current_user),
) -> UserModel:
    """Ensure the current user is active."""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


async def rate_limit_general() -> None:
    """Basic rate limiting for general API routes."""
    limiter = RateLimiters.api_general
    try:
        allowed = await limiter.allow_request("global")
    except RuntimeError:
        # Redis not available; skip rate limiting
        return
    if not allowed:
        raise HTTPException(status_code=429, detail="Too Many Requests")
