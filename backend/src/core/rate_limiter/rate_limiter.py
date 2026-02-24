import random
from time import time

from redis.asyncio import Redis


class RateLimiter:
    def __init__(self, redis: Redis):
        self._redis = redis

    async def is_limited(
        self,
        identifier: str,
        endpoint: str,
        windows: list[tuple[int, int]],
    ) -> bool:
        key = f"rate_limiter:{endpoint}:{identifier}"

        current_ms = time() * 1000
        current_request = f"{current_ms}--{random.randint(0, 100_000)}"

        max_window_seconds = max(ws for (_, ws) in windows)
        oldest_window_start_ms = current_ms - max_window_seconds * 1000

        async with self._redis.pipeline() as pipe:
            await pipe.zremrangebyscore(
                name=key,
                min=0,
                max=oldest_window_start_ms,
            )

            for _, ws in windows:
                window_start_ms = current_ms - ws * 1000
                await pipe.zcount(key, window_start_ms, "+inf")

            await pipe.zadd(key, {current_request: current_ms})
            await pipe.expire(key, max_window_seconds)

            res = await pipe.execute()

        counts = res[1: 1 + len(windows)]
        for (max_requests, _), count in zip(windows, counts, strict=False):
            if count >= max_requests:
                return True

        return False
