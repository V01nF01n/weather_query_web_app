from sqlalchemy import Boolean, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class WeatherDetail(Base):
    __tablename__ = "weather_details"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    query_record_id: Mapped[int] = mapped_column(
        ForeignKey("query_records.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )
    temperature: Mapped[float] = mapped_column(Float, nullable=False)
    feels_like: Mapped[float | None] = mapped_column(Float, nullable=True)
    humidity: Mapped[int | None] = mapped_column(Integer, nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    unit: Mapped[str] = mapped_column(String(16), nullable=False)
    served_from_cache: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )
    raw_payload: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        default=dict
    )

    query_record: Mapped["QueryRecord"] = relationship(
        back_populates="detail"
    )