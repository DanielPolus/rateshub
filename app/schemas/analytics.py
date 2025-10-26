from pydantic import BaseModel
from typing import Optional

class AnalyticsSummaryOut(BaseModel):
    base: str
    quote: str
    start: str
    end: str
    count: int
    min: Optional[float] = None
    max: Optional[float] = None
    avg: Optional[float] = None
    stddev: Optional[float] = None
    change_abs: Optional[float] = None
    change_pct: Optional[float] = None
    last_rate: Optional[float] = None
    first_rate: Optional[float] = None
