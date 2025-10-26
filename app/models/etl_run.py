from datetime import datetime
from sqlalchemy import DateTime, String, Integer, func
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base
from typing import Optional

class ETLRun(Base):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    job: Mapped[str] = mapped_column(String(32))
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), server_default=func.now(), nullable=False
    )
    finished_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=False), nullable=True
    )
    status: Mapped[str] = mapped_column(String(16), default="started")
    rows_ingested: Mapped[int] = mapped_column(Integer, default=0)
    error_text: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
