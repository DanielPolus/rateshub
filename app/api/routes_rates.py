from datetime import date
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session

from app.core.db import SessionLocal
from app.core.timeutil import window_to_dates
from app.core.cache import cache_get_json, cache_set_json
from app.schemas.rate import RateOut
from app.services.rates_service import get_rates, get_latest_rate, serialize_rates
from typing import Optional

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/", response_model=list[RateOut])
def list_rates(
    base: str,
    quote: str,
    start: Optional[date] = Query(default=None),
    end: Optional[date] = Query(default=None),
    last: Optional[str] = Query(default=None, description="пример: 30d, 7d, 1w, 1m"),
    db: Session = Depends(get_db),
):
    """
    Правила:
    - Если передан last=..., игнорируем start/end и используем окно (кэшируем ответ).
    - Если переданы start/end — идём в БД напрямую без кэша (можно тоже кэшировать позже).
    """
    # Вариант 1: last=...  -> быстрый путь через Redis
    if last:
        s, e = window_to_dates(last)
        cache_key = f"rates:{base}:{quote}:{s.isoformat()}_{e.isoformat()}"
        cached = cache_get_json(cache_key)
        if cached is not None:
            return cached  # это уже сериализованный список

        rows = get_rates(db, base, quote, s, e)
        data = serialize_rates(rows)
        # TTL 5 минут: если твой ETL часовой — хватит. Можно поднять до 10–15 минут.
        cache_set_json(cache_key, data, ttl_seconds=300)
        return data

    # Вариант 2: ручные start/end
    rows = get_rates(db, base, quote, start, end)
    return serialize_rates(rows)

@router.get("/latest", response_model=Optional[RateOut])
def latest_rate(base: str, quote: str, db: Session = Depends(get_db)):
    row = get_latest_rate(db, base, quote)
    if not row:
        return None
    return {
        "date": row.date,
        "base": row.base,
        "quote": row.quote,
        "rate": row.rate,
        "source": row.source,
    }
