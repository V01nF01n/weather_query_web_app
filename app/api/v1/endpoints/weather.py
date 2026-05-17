from typing import Literal

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse

from app.dependencies import get_query_service
from app.schemas.weather import Unit, WeatherRequest, WeatherResponse
from app.services.query_service import QueryService

router = APIRouter(prefix="/api")


def _client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    client = request.client
    return client.host if client else "unknown"


@router.get("/weather", response_model=WeatherResponse)
async def fetch_weather_api(request: Request, city: str, unit: Unit = "celsius", service: QueryService = Depends(get_query_service)) -> WeatherResponse:
    return await service.fetch_weather(city=city, unit=unit, client_ip=_client_ip(request))


@router.post("/weather", response_class=HTMLResponse)
async def fetch_weather_html(
    request: Request,
    city: str = Form(...),
    unit: Literal["celsius", "fahrenheit"] = Form("celsius"),
    service: QueryService = Depends(get_query_service),
) -> HTMLResponse:
    result = await service.fetch_weather(city=city, unit=unit, client_ip=_client_ip(request))
    template = request.app.state.templates.get_template("result.html")
    html = template.render(result=result.model_dump(), city=city)
    return HTMLResponse(html)
