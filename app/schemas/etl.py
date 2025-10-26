from pydantic import BaseModel
from datetime import datetime, date
from typing import Optional

class ETLRunOut(BaseModel):
    id: int
    job: str
    started_at: datetime
    finished_at: Optional[datetime] = None
    status: str
    rows_ingested: int
    error_text: Optional[str] = None

class FreshnessOut(BaseModel):
    base: str
    quote: str
    max_date: Optional[date] = None
