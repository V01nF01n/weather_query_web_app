from dataclasses import dataclass
from datetime import date

from app.repositories.query_repository import QueryRepository
from app.schemas.weather import HistoryItem, HistoryPage, Unit, WeatherResponse
from app.services.cache_service import CacheService
from app.services.rate_limiter import RateLimiter
from app.services.weather_client import WeatherClient


@dataclass(slots=True)
class QueryService:
    repo: QueryRepository
    cache: CacheService
    weather_client: WeatherClient
    limiter: RateLimiter

    async def fetch_weather(self, *, city: str, unit: Unit, client_ip: str) -> WeatherResponse:
        await self.limiter.check(client_ip)
        cached = await self.cache.get(city, unit)
        if cached is not None:
            payload = cached.model_copy(update={"served_from_cache": True})
            await self.repo.create(
                city_name=payload.city_name,
                temperature=payload.temperature,
                feels_like=payload.feels_like,
                humidity=payload.humidity,
                description=payload.description,
                unit=payload.unit,
                served_from_cache=True,
                raw_payload=payload.model_dump(mode="json"),
            )
            return payload

        fresh = await self.weather_client.fetch(city=city, unit=unit)
        await self.cache.set(city, unit, fresh)
        await self.repo.create(
            city_name=fresh.city_name,
            temperature=fresh.temperature,
            feels_like=fresh.feels_like,
            humidity=fresh.humidity,
            description=fresh.description,
            unit=fresh.unit,
            served_from_cache=False,
            raw_payload=fresh.model_dump(mode="json"),
        )
        return fresh

    async def history(self, *, page: int, page_size: int, city: str | None = None, date_from: date | None = None, date_to: date | None = None) -> HistoryPage:
        total = await self.repo.count(city=city, date_from=date_from, date_to=date_to)
        items = await self.repo.list(page=page, page_size=page_size, city=city, date_from=date_from, date_to=date_to)
        pages = max((total + page_size - 1) // page_size, 1) if total else 0
        history_items: list[HistoryItem] = []
        for item in items:
            detail = item.detail
            history_items.append(
                HistoryItem(
                    id=item.id,
                    city_name=item.city_name,
                    queried_at=item.queried_at,
                    temperature=detail.temperature,
                    feels_like=detail.feels_like,
                    humidity=detail.humidity,
                    description=detail.description,
                    unit=detail.unit,
                    served_from_cache=detail.served_from_cache,
                )
            )
        return HistoryPage(items=history_items, total=total, page=page, page_size=page_size, pages=pages)
