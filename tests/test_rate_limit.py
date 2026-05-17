import pytest
from fastapi import HTTPException

from app.schemas.weather import WeatherResponse
from app.services.query_service import QueryService
from tests.conftest import FakeCache, FakeLimiter, FakeRepo, FakeWeatherClient


@pytest.mark.asyncio
async def test_rate_limit_blocks_before_db_write():
    repo = FakeRepo()
    cache = FakeCache()
    weather_client = FakeWeatherClient(payload=WeatherResponse(city_name="Paris", temperature=12.0, feels_like=11.0, humidity=60, description="rain", unit="celsius"))
    limiter = FakeLimiter(blocked=True)
    service = QueryService(repo=repo, cache=cache, weather_client=weather_client, limiter=limiter)

    with pytest.raises(HTTPException) as exc:
        await service.fetch_weather(city="Paris", unit="celsius", client_ip="127.0.0.1")

    assert exc.value.status_code == 429
    assert repo.created == []
    assert weather_client.calls == 0
