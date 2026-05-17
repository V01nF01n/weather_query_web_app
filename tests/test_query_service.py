import pytest

from app.schemas.weather import WeatherResponse
from app.services.query_service import QueryService
from tests.conftest import FakeCache, FakeLimiter, FakeRepo, FakeWeatherClient


@pytest.mark.asyncio
async def test_cache_reuse_skips_fresh_fetch():
    repo = FakeRepo()
    cached = WeatherResponse(city_name="London", temperature=10.0, feels_like=8.0, humidity=70, description="clear sky", unit="celsius")
    cache = FakeCache(storage={("london", "celsius"): cached})
    weather_client = FakeWeatherClient(payload=cached)
    limiter = FakeLimiter()
    service = QueryService(repo=repo, cache=cache, weather_client=weather_client, limiter=limiter)

    result = await service.fetch_weather(city="London", unit="celsius", client_ip="127.0.0.1")

    assert result.served_from_cache is True
    assert weather_client.calls == 0
    assert len(repo.created) == 1
    assert repo.created[0]["served_from_cache"] is True


@pytest.mark.asyncio
async def test_fresh_fetch_writes_cache_and_db():
    repo = FakeRepo()
    payload = WeatherResponse(city_name="Berlin", temperature=11.0, feels_like=9.0, humidity=50, description="cloudy", unit="celsius")
    cache = FakeCache()
    weather_client = FakeWeatherClient(payload=payload)
    limiter = FakeLimiter()
    service = QueryService(repo=repo, cache=cache, weather_client=weather_client, limiter=limiter)

    result = await service.fetch_weather(city="Berlin", unit="celsius", client_ip="127.0.0.1")

    assert result.served_from_cache is False
    assert weather_client.calls == 1
    assert len(repo.created) == 1
    assert await cache.get("Berlin", "celsius") is not None
