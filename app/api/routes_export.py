from datetime import date
from io import BytesIO, StringIO

import pandas as pd
from fastapi import APIRouter, Depends, Query, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import Optional

from app.core.db import SessionLocal
from app.core.timeutil import window_to_dates
from app.services.rates_service import get_rates, serialize_rates

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def _fetch_df(db: Session, base: str, quote: str, start: date, end: date) -> pd.DataFrame:
    rows = get_rates(db, base, quote, start, end)
    data = serialize_rates(rows)
    df = pd.DataFrame(data)
    return df[["date", "base", "quote", "rate", "source"]]

@router.get("/csv")
def export_csv(
    base: str,
    quote: str,
    last: Optional[str] = Query(default="30d"),
    start: Optional[date] = None,
    end: Optional[date] = None,
    db: Session = Depends(get_db),
):
    if last:
        s, e = window_to_dates(last)
    else:
        if not (start and end):
            raise HTTPException(status_code=400, detail="Provide either last=... or both start & end")
        s, e = start, end

    df = _fetch_df(db, base, quote, s, e)
    buf = StringIO()
    df.to_csv(buf, index=False)
    buf.seek(0)
    filename = f"rates_{base}_{quote}_{s.isoformat()}_{e.isoformat()}.csv"
    return StreamingResponse(
        buf, media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )

@router.get("/parquet")
def export_parquet(
    base: str,
    quote: str,
    last: Optional[str] = Query(default="30d"),
    start: Optional[date] = None,
    end: Optional[date] = None,
    db: Session = Depends(get_db),
):
    if last:
        s, e = window_to_dates(last)
    else:
        if not (start and end):
            raise HTTPException(status_code=400, detail="Provide either last=... or both start & end")
        s, e = start, end

    df = _fetch_df(db, base, quote, s, e)
    buf = BytesIO()
    df.to_parquet(buf, index=False)
    buf.seek(0)
    filename = f"rates_{base}_{quote}_{s.isoformat()}_{e.isoformat()}.parquet"
    return StreamingResponse(
        buf, media_type="application/octet-stream",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )
