from datetime import date

import pytest

from app.schemas.weather import WeatherResponse
from app.services.query_service import QueryService
from tests.conftest import FakeCache, FakeLimiter, FakeRepo, FakeWeatherClient


@pytest.mark.asyncio
async def test_history_filters_and_pagination_are_passed_to_repo():
    repo = FakeRepo(total=17, items=[])
    service = QueryService(
        repo=repo,
        cache=FakeCache(),
        weather_client=FakeWeatherClient(payload=WeatherResponse(city_name="X", temperature=0.0, feels_like=None, humidity=None, description="ok", unit="celsius")),
        limiter=FakeLimiter(),
    )
    page = await service.history(page=2, page_size=10, city="lon", date_from=date(2026, 1, 1), date_to=date(2026, 1, 31))

    assert page.page == 2
    assert page.page_size == 10
    assert page.pages == 2
    assert page.total == 17
