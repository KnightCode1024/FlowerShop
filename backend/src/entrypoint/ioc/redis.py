from dishka import Provider, Scope, provide
from redis.asyncio import Redis

from entrypoint.config import Config


class RedisProvider(Provider):
    scope = Scope.APP

    @provide
    def get_redis(self, config: Config) -> Redis:
        return Redis(
            host=config.redis.HOST,
            port=config.redis.PORT,
        )
