import logging
import time
import uuid
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.api.v1.routes import router as api_router
from app.core.config import get_settings
from app.core.logging import configure_logging
from app.dependencies import close_redis, create_redis
from redis.asyncio import Redis

settings = get_settings()
configure_logging(settings.debug)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.templates = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))
    app.state.redis = create_redis(settings)
    try:
        yield
    finally:
        redis: Redis = app.state.redis
        await close_redis(redis)


app = FastAPI(title=settings.app_name, debug=settings.debug, lifespan=lifespan)
app.include_router(api_router)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    request_id = str(uuid.uuid4())
    start = time.perf_counter()
    client_ip = request.headers.get("x-forwarded-for", request.client.host if request.client else "unknown")
    logger.info("request start", extra={"event": "request_start", "request_id": request_id, "method": request.method, "path": request.url.path, "client_ip": client_ip})
    try:
        response = await call_next(request)
    except Exception:
        logger.exception("request error", extra={"event": "request_error", "request_id": request_id, "method": request.method, "path": request.url.path, "client_ip": client_ip})
        raise
    duration_ms = int((time.perf_counter() - start) * 1000)
    logger.info(
        "request end",
        extra={
            "event": "request_end",
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "duration_ms": duration_ms,
            "client_ip": client_ip,
        },
    )
    return response


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    template = request.app.state.templates.get_template("index.html")
    return HTMLResponse(template.render(title=settings.app_name))
