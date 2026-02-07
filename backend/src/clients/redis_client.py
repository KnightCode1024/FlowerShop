from functools import lru_cache

from redis.asyncio import Redis

from entrypoint.config import Config


class RedisClient:
    def __init__(self, config: Config):
        self.redis = Redis(
            host=config.redis.HOST,
            port=config.redis.PORT,
        )

    @lru_cache
    def get_redis(self):
        return self.redis
