from datetime import date
from sqlalchemy import select, func, and_
from sqlalchemy.orm import Session
from app.models.rate import Rate
from app.models.etl_run import ETLRun
from typing import Optional

def list_etl_runs(db: Session, limit: int = 20):
    stmt = select(ETLRun).order_by(ETLRun.started_at.desc()).limit(limit)
    return db.execute(stmt).scalars().all()

def pair_freshness(db: Session, base: str, quote: str) -> Optional[date]:
    stmt = select(func.max(Rate.date)).where(and_(Rate.base == base, Rate.quote == quote))
    return db.execute(stmt).scalar()

def all_pairs_freshness(db: Session, bases: list[str], quotes: list[str]) -> list[tuple[str, str, Optional[date]]]:
    out = []
    for b in bases:
        for q in quotes:
            if b == q:
                continue
            out.append((b, q, pair_freshness(db, b, q)))
    return out
