import logging
from dataclasses import dataclass
from time import perf_counter

import httpx

from app.core.config import Settings
from app.schemas.weather import Unit, WeatherResponse

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class WeatherClient:
    settings: Settings
    client: httpx.AsyncClient

    async def fetch(self, city: str, unit: Unit) -> WeatherResponse:
        units_param = "metric" if unit == "celsius" else "imperial"
        url = f"{self.settings.openweather_base_url.rstrip('/')}/weather"
        params = {
            "q": city,
            "appid": self.settings.openweather_api_key,
            "units": units_param,
            "lang": "en",
        }
        started = perf_counter()
        response = await self.client.get(url, params=params)
        elapsed_ms = int((perf_counter() - started) * 1000)
        logger.info("external weather api call", extra={"event": "external_api", "external_ms": elapsed_ms})
        response.raise_for_status()
        payload = response.json()
        weather = payload["weather"][0]
        main = payload["main"]
        return WeatherResponse(
            city_name=payload["name"],
            temperature=float(main["temp"]),
            feels_like=float(main.get("feels_like")) if main.get("feels_like") is not None else None,
            humidity=int(main.get("humidity")) if main.get("humidity") is not None else None,
            description=str(weather["description"]),
            unit=unit,
            served_from_cache=False,
        )
