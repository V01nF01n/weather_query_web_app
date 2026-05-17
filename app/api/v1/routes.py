from fastapi import APIRouter

from app.api.v1.endpoints import health, history, weather

router = APIRouter()
router.include_router(weather.router, tags=["weather"])
router.include_router(history.router, tags=["history"])
router.include_router(health.router, tags=["health"])