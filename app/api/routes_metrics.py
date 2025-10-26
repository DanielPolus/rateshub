from datetime import datetime, timezone
from typing import List

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.core.db import SessionLocal
from app.schemas.etl import ETLRunOut, FreshnessOut
from app.services.etl_service import list_etl_runs, all_pairs_freshness
from app.models.etl_run import ETLRun
from app.models.rate import Rate

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/etl", response_model=List[ETLRunOut])
def etl_metrics(limit: int = 20, db: Session = Depends(get_db)):
    runs = list_etl_runs(db, limit=limit)
    return [
        {
            "id": r.id,
            "job": r.job,
            "started_at": r.started_at,
            "finished_at": r.finished_at,
            "status": r.status,
            "rows_ingested": r.rows_ingested,
            "error_text": r.error_text,
        }
        for r in runs
    ]

@router.get("/freshness", response_model=List[FreshnessOut])
def freshness(
    bases: str = "EUR",
    quotes: str = "USD,GBP,PLN,RON",
    db: Session = Depends(get_db),
):
    b_list = [b.strip().upper() for b in bases.split(",") if b.strip()]
    q_list = [q.strip().upper() for q in quotes.split(",") if q.strip()]

    res = all_pairs_freshness(db, b_list, q_list)
    return [{"base": b, "quote": q, "max_date": d} for (b, q, d) in res]

@router.get("/health")
def health():
    return {"status": "ok", "time_utc": datetime.now(timezone.utc).isoformat()}

@router.get("/scheduler")
def scheduler_status(db: Session = Depends(get_db)):
    last_run = db.execute(
        select(ETLRun).order_by(ETLRun.started_at.desc()).limit(1)
    ).scalar_one_or_none()

    now_utc = datetime.now(timezone.utc)

    if not last_run:
        max_date = db.execute(select(func.max(Rate.date))).scalar()
        return {
            "status": "unknown",
            "message": "no ETL runs yet",
            "last_run_started_at": None,
            "last_run_finished_at": None,
            "age_minutes": None,
            "duration_seconds": None,
            "rows_ingested": 0,
            "data_max_date": max_date.isoformat() if max_date else None,
        }

    if last_run.finished_at is None or last_run.status == "started":
        ref_time = last_run.started_at.replace(tzinfo=timezone.utc) if last_run.started_at.tzinfo is None else last_run.started_at
        age_min = (now_utc - ref_time).total_seconds() / 60.0
        max_date = db.execute(select(func.max(Rate.date))).scalar()

        return {
            "status": "running",
            "last_run_started_at": last_run.started_at.isoformat(),
            "last_run_finished_at": None,
            "age_minutes": round(age_min, 2),
            "duration_seconds": None,
            "rows_ingested": last_run.rows_ingested,
            "data_max_date": max_date.isoformat() if max_date else None,
        }

    finished = last_run.finished_at
    started_utc = last_run.started_at.replace(tzinfo=timezone.utc) if last_run.started_at.tzinfo is None else last_run.started_at
    finished_utc = finished.replace(tzinfo=timezone.utc) if finished.tzinfo is None else finished

    age_min = (now_utc - finished_utc).total_seconds() / 60.0
    duration_sec = max(0.0, (finished_utc - started_utc).total_seconds())

    healthy = (last_run.status == "ok") and (age_min < 3.0)

    max_date = db.execute(select(func.max(Rate.date))).scalar()

    return {
        "status": "healthy" if healthy else "stale",
        "last_run_started_at": last_run.started_at.isoformat(),
        "last_run_finished_at": last_run.finished_at.isoformat() if last_run.finished_at else None,
        "age_minutes": round(age_min, 2),
        "duration_seconds": round(duration_sec, 2),
        "rows_ingested": last_run.rows_ingested,
        "data_max_date": max_date.isoformat() if max_date else None,
        "last_run_status": last_run.status,
        "last_error": last_run.error_text,
    }
