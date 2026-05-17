from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    database: bool
    external_api: bool | None = None
