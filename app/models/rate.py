from datetime import date
from sqlalchemy import String, Date, Float, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base

class Rate(Base):
    __table_args__ = (
        UniqueConstraint("date", "base", "quote", "source", name="uq_rates_bq_date_src"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    date: Mapped[date] = mapped_column(Date, index=True, nullable=False)
    base: Mapped[str] = mapped_column(String(10), index=True)
    quote: Mapped[str] = mapped_column(String(10), index=True)
    rate: Mapped[float] = mapped_column(Float)
    source: Mapped[str] = mapped_column(String(32), default="frankfurter")
