import csv
from datetime import date
from io import StringIO

from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import HTMLResponse, StreamingResponse

from app.core.config import get_settings
from app.dependencies import get_query_service
from app.services.query_service import QueryService

router = APIRouter()


@router.get("/api/history")
async def history_api(
    service: QueryService = Depends(get_query_service),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    city: str | None = None,
    date_from: date | None = Query(default=None, alias="from"),
    date_to: date | None = Query(default=None, alias="to"),
):
    return await service.history(page=page, page_size=page_size, city=city, date_from=date_from, date_to=date_to)


@router.get("/history", response_class=HTMLResponse)
async def history_page(
    request: Request,
    service: QueryService = Depends(get_query_service),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    city: str | None = None,
    date_from: date | None = Query(default=None, alias="from"),
    date_to: date | None = Query(default=None, alias="to"),
):
    history = await service.history(page=page, page_size=page_size, city=city, date_from=date_from, date_to=date_to)
    template = request.app.state.templates.get_template("history.html")
    html = template.render(history=history.model_dump(mode="json"), filters={"city": city or "", "from": date_from.isoformat() if date_from else "", "to": date_to.isoformat() if date_to else ""})
    return HTMLResponse(html)


@router.get("/export.csv")
async def export_csv(
    service: QueryService = Depends(get_query_service),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=1000, ge=1, le=1000),
    city: str | None = None,
    date_from: date | None = Query(default=None, alias="from"),
    date_to: date | None = Query(default=None, alias="to"),
):
    history = await service.history(page=page, page_size=page_size, city=city, date_from=date_from, date_to=date_to)
    buffer = StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["id", "city_name", "queried_at", "temperature", "feels_like", "humidity", "description", "unit", "served_from_cache"])
    for item in history.items:
        writer.writerow([
            item.id,
            item.city_name,
            item.queried_at,
            item.temperature,
            item.feels_like,
            item.humidity,
            item.description,
            item.unit,
            item.served_from_cache,
        ])
    buffer.seek(0)
    return StreamingResponse(iter([buffer.getvalue()]), media_type="text/csv", headers={"Content-Disposition": "attachment; filename=history.csv"})
