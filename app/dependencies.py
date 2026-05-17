from collections.abc import AsyncIterator

import httpx
from fastapi import Depends, Request
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings, get_settings
from app.db.session import get_session
from app.repositories.query_repository import QueryRepository
from app.services.cache_service import CacheService
from app.services.query_service import QueryService
from app.services.rate_limiter import RateLimiter
from app.services.weather_client import WeatherClient


def create_redis(settings: Settings) -> Redis:
    return Redis.from_url(settings.redis_url, decode_responses=False)


async def close_redis(redis: Redis) -> None:
    await redis.aclose()


def get_redis(request: Request) -> Redis:
    return request.app.state.redis


async def get_http_client(settings: Settings = Depends(get_settings)) -> AsyncIterator[httpx.AsyncClient]:
    timeout = httpx.Timeout(settings.external_api_timeout_seconds)
    async with httpx.AsyncClient(timeout=timeout) as client:
        yield client


async def get_query_repository(session: AsyncSession = Depends(get_session)) -> QueryRepository:
    return QueryRepository(session)


async def get_cache_service(redis: Redis = Depends(get_redis), settings: Settings = Depends(get_settings)) -> CacheService:
    return CacheService(redis=redis, ttl_seconds=settings.cache_ttl_seconds)


async def get_rate_limiter(redis: Redis = Depends(get_redis), settings: Settings = Depends(get_settings)) -> RateLimiter:
    return RateLimiter(redis=redis, limit_per_minute=settings.rate_limit_per_minute)


async def get_weather_client(client: httpx.AsyncClient = Depends(get_http_client), settings: Settings = Depends(get_settings)) -> WeatherClient:
    return WeatherClient(settings=settings, client=client)


async def get_query_service(
    repo: QueryRepository = Depends(get_query_repository),
    cache: CacheService = Depends(get_cache_service),
    weather_client: WeatherClient = Depends(get_weather_client),
    limiter: RateLimiter = Depends(get_rate_limiter),
) -> QueryService:
    return QueryService(repo=repo, cache=cache, weather_client=weather_client, limiter=limiter)
