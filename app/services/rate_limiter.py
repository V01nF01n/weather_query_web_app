from dataclasses import dataclass

from fastapi import HTTPException, status
from redis.asyncio import Redis


@dataclass(slots=True)
class RateLimiter:
    redis: Redis
    limit_per_minute: int

    def _key(self, client_ip: str) -> str:
        return f"rate_limit:{client_ip}"

    async def check(self, client_ip: str) -> None:
        key = self._key(client_ip)
        current = await self.redis.incr(key)
        if current == 1:
            await self.redis.expire(key, 60)
        ttl = await self.redis.ttl(key)
        if current > self.limit_per_minute:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded. Please try again in {max(ttl, 1)} seconds.",
            )
