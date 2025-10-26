from datetime import date
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import Optional

from app.core.db import SessionLocal
from app.core.timeutil import window_to_dates
from app.core.cache import cache_get_json, cache_set_json
from app.schemas.analytics import AnalyticsSummaryOut
from app.services.analytics_service import analytics_summary

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/summary", response_model=AnalyticsSummaryOut)
def summary(
        base: str,
        quote: str,
        start: Optional[date] = Query(default=None),
        end: Optional[date] = Query(default=None),
        last: Optional[str] = Query(default=None, description="Example: 30d, 7d, 1w, 1n"),
        db: Session = Depends(get_db),
):
    if last:
        start_d, end_d = window_to_dates(last)
    else:
        if not (start and end):
            raise HTTPException(status_code=400, detail="Provide either last=... or both start & end")
        start_d, end_d = start, end

    cache_key = f"analytics:{base}:{quote}:{start_d.isoformat()}_{end_d.isoformat()}"
    cached = cache_get_json(cache_key)
    if cached is not None:
        return cached

    data = analytics_summary(db, base, quote, start_d, end_d)
    cache_set_json(cache_key, data, ttl_seconds=300)
    return data
