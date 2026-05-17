from datetime import datetime
from sqlalchemy import DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class QueryRecord(Base):
    __tablename__ = "query_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    city_name: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    queried_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        index=True
    )

    detail: Mapped["WeatherDetail"] = relationship(
        back_populates="query_record",
        cascade="all, delete-orphan",
        uselist=False,
    )