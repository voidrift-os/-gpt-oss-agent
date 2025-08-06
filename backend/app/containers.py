"""Simple dependency container used for testing and configuration."""

from __future__ import annotations

from typing import Any, Awaitable, Callable

from app.core.config import Settings
from app.core.redis import RedisManager
from app.db.session import async_session


class Provider:
    """Minimal async provider with override capability."""

    def __init__(self, func: Callable[..., Awaitable[Any]]):
        self._func = func
        self._override: Callable[..., Awaitable[Any]] | None = None

    def override(self, func: Callable[..., Awaitable[Any]]) -> None:
        self._override = func

    def reset_override(self) -> None:
        self._override = None

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        func = self._override or self._func
        return func(*args, **kwargs)


class Container:
    """Lightweight container holding application singletons."""

    def __init__(self) -> None:
        self.config = Settings()
        self.redis_manager = RedisManager()
        self.db = Provider(async_session)


# Global container instance used by the application
container = Container()

