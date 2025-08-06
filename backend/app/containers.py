from dependency_injector import containers, providers

from app.core.config import Settings
from app.core.redis import RedisManager
from app.db.session import async_session


class Container(containers.DeclarativeContainer):

    config = providers.Singleton(Settings)

    redis_manager = providers.Singleton(RedisManager)

    db = providers.Singleton(async_session)


container = Container()
