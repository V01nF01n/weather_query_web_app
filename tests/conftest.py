from dataclasses import dataclass, field

import pytest

from app.schemas.weather import Unit, WeatherResponse


@dataclass
class FakeCache:
    storage: dict[tuple[str, Unit], WeatherResponse] = field(default_factory=dict)

    async def get(self, city: str, unit: Unit):
        return self.storage.get((city.strip().lower(), unit))

    async def set(self, city: str, unit: Unit, payload: WeatherResponse):
        self.storage[(city.strip().lower(), unit)] = payload


@dataclass
class FakeWeatherClient:
    payload: WeatherResponse
    calls: int = 0

    async def fetch(self, city: str, unit: Unit):
        self.calls += 1
        return self.payload.model_copy(update={"city_name": city, "unit": unit})


@dataclass
class FakeLimiter:
    limit: int = 30
    blocked: bool = False
    calls: int = 0

    async def check(self, client_ip: str):
        self.calls += 1
        if self.blocked:
            from fastapi import HTTPException, status
            raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Rate limit exceeded")


@dataclass
class FakeRepo:
    created: list[dict] = field(default_factory=list)
    items: list = field(default_factory=list)
    total: int = 0

    async def create(self, **kwargs):
        self.created.append(kwargs)
        return kwargs

    async def count(self, **kwargs):
        return self.total

    async def list(self, **kwargs):
        return self.items
