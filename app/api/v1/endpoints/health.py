import httpx
from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.db.session import get_session
from app.schemas.health import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health(session: AsyncSession = Depends(get_session)) -> HealthResponse:
    db_ok = False
    try:
        await session.execute(text("select 1"))
        db_ok = True
    except Exception:
        db_ok = False

    settings = get_settings()
    external_ok: bool | None = None
    if settings.openweather_api_key:
        try:
            timeout = httpx.Timeout(1.5)
            async with httpx.AsyncClient(timeout=timeout) as client:
                resp = await client.get(
                    f"{settings.openweather_base_url.rstrip('/')}/weather",
                    params={"q": "London", "appid": settings.openweather_api_key, "units": "metric"},
                )
                external_ok = resp.status_code in {200, 401, 404, 429}
        except Exception:
            external_ok = False

    status = "ok" if db_ok else "degraded"
    return HealthResponse(status=status, database=db_ok, external_api=external_ok)
