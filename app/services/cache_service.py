import json
from dataclasses import dataclass

from redis.asyncio import Redis

from app.schemas.weather import WeatherResponse, Unit


@dataclass(slots=True)
class CacheService:
    redis: Redis
    ttl_seconds: int

    @staticmethod
    def _key(city: str, unit: Unit) -> str:
        normalized = city.strip().lower()
        return f"weather:{unit}:{normalized}"

    async def get(self, city: str, unit: Unit) -> WeatherResponse | None:
        raw = await self.redis.get(self._key(city, unit))
        if raw is None:
            return None
        if isinstance(raw, bytes):
            raw = raw.decode("utf-8")
        data = json.loads(raw)
        return WeatherResponse.model_validate(data)

    async def set(self, city: str, unit: Unit, payload: WeatherResponse) -> None:
        await self.redis.set(self._key(city, unit), payload.model_dump_json(), ex=self.ttl_seconds)
