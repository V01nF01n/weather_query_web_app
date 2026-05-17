from datetime import date, datetime, time, timezone
from typing import Any

from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.models.query_record import QueryRecord
from app.models.weather_detail import WeatherDetail


class QueryRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(
        self,
        *,
        city_name: str,
        temperature: float,
        feels_like: float | None,
        humidity: int | None,
        description: str,
        unit: str,
        served_from_cache: bool,
        raw_payload: dict[str, Any],
    ) -> QueryRecord:
        record = QueryRecord(city_name=city_name)
        record.detail = WeatherDetail(
            temperature=temperature,
            feels_like=feels_like,
            humidity=humidity,
            description=description,
            unit=unit,
            served_from_cache=served_from_cache,
            raw_payload=raw_payload,
        )
        self.session.add(record)
        await self.session.commit()
        await self.session.refresh(record)
        return record

    @staticmethod
    def _apply_filters(stmt: Select[tuple[QueryRecord]], *, city: str | None, date_from: date | None, date_to: date | None) -> Select[tuple[QueryRecord]]:
        if city:
            stmt = stmt.where(QueryRecord.city_name.ilike(f"%{city.strip()}%"))
        if date_from:
            start_dt = datetime.combine(date_from, time.min, tzinfo=timezone.utc)
            stmt = stmt.where(QueryRecord.queried_at >= start_dt)
        if date_to:
            end_dt = datetime.combine(date_to, time.max, tzinfo=timezone.utc)
            stmt = stmt.where(QueryRecord.queried_at <= end_dt)
        return stmt

    async def count(self, *, city: str | None = None, date_from: date | None = None, date_to: date | None = None) -> int:
        stmt = select(func.count()).select_from(QueryRecord)
        stmt = self._apply_filters(stmt, city=city, date_from=date_from, date_to=date_to)
        result = await self.session.execute(stmt)
        return int(result.scalar_one())

    async def list(self, *, page: int, page_size: int, city: str | None = None, date_from: date | None = None, date_to: date | None = None) -> list[QueryRecord]:
        offset = (page - 1) * page_size
        stmt = select(QueryRecord).options(joinedload(QueryRecord.detail))
        stmt = self._apply_filters(stmt, city=city, date_from=date_from, date_to=date_to)
        stmt = stmt.order_by(QueryRecord.queried_at.desc(), QueryRecord.id.desc()).offset(offset).limit(page_size)
        result = await self.session.execute(stmt)
        return list(result.scalars().unique().all())