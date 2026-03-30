from dishka import Provider, Scope, provide
from redis.asyncio import Redis

from core.rate_limiter import RateLimiter


class RateLimiterProvider(Provider):
    scope = Scope.REQUEST

    @provide
    def get_rate_limiter(self, redis: Redis) -> RateLimiter:
        return RateLimiter(redis)
