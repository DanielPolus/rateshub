from datetime import date
from fastapi import APIRouter, Request, Query, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.core.db import SessionLocal
from app.core.timeutil import window_to_dates
from app.services.rates_service import get_rates, serialize_rates
from app.services.analytics_service import analytics_summary
from app.models.etl_run import ETLRun

router = APIRouter()
templates = Jinja2Templates(directory="templates")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/dashboard", response_class=HTMLResponse)
def dashboard(
    request: Request,
    base: str = "EUR",
    quote: str = "USD",
    last: str = "30d",
    db: Session = Depends(get_db),
):
    start_d, end_d = window_to_dates(last)

    rows = get_rates(db, base, quote, start_d, end_d)
    data = serialize_rates(rows)
    summary = analytics_summary(db, base, quote, start_d, end_d)

    last_run = db.query(ETLRun).order_by(ETLRun.finished_at.desc()).first()

    if last_run:
        from datetime import datetime, timezone
        now_utc = datetime.now(timezone.utc)
        if last_run.finished_at:
            age_min = (now_utc - last_run.finished_at.replace(tzinfo=timezone.utc)).total_seconds() / 60
        else:
            age_min = None

        scheduler = {
            "status": (
                "running"
                if last_run.finished_at is None
                else "healthy"
                if age_min is not None and age_min < 3
                else "stale"
            ),
            "finished_at": last_run.finished_at,
            "rows_ingested": last_run.rows_ingested,
            "age_min": round(age_min, 1) if age_min else None,
        }
    else:
        scheduler = {"status": "unknown", "finished_at": None, "rows_ingested": 0}

    REQUIRED_KEYS = [
        "base", "quote", "start", "end", "count",
        "min", "max", "avg", "stddev", "first_rate", "last_rate", "change_abs", "change_pct",
    ]
    for k in REQUIRED_KEYS:
        summary.setdefault(k, None)

    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "base": base,
            "quote": quote,
            "last": last,
            "series": data,
            "summary": summary,
            "scheduler": scheduler,
        },
    )

