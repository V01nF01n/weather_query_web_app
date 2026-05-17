from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

Unit = Literal["celsius", "fahrenheit"]


class WeatherRequest(BaseModel):
    city: str = Field(min_length=1, max_length=255)
    unit: Unit = "celsius"


class WeatherResponse(BaseModel):
    city_name: str
    temperature: float
    feels_like: float | None = None
    humidity: int | None = None
    description: str
    unit: Unit
    served_from_cache: bool = False
    queried_at: datetime | None = None


class HistoryItem(BaseModel):
    id: int
    city_name: str
    queried_at: datetime
    temperature: float
    feels_like: float | None = None
    humidity: int | None = None
    description: str
    unit: Unit
    served_from_cache: bool


class HistoryPage(BaseModel):
    items: list[HistoryItem]
    total: int
    page: int
    page_size: int
    pages: int