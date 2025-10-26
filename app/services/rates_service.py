from datetime import date
from sqlalchemy import select, and_, func, desc
from sqlalchemy.orm import Session
from app.models.rate import Rate
from typing import Optional

def get_rates(db: Session, base: str, quote: str, start: Optional[date], end: Optional[date]):
    conds = [Rate.base == base, Rate.quote == quote]
    if start:
        conds.append(Rate.date >= start)
    if end:
        conds.append(Rate.date <= end)

    stmt = select(Rate).where(and_(*conds)).order_by(Rate.date.asc())
    return db.execute(stmt).scalars().all()

def get_latest_rate(db: Session, base: str, quote: str):
    stmt = (
        select(Rate)
        .where(and_(Rate.base == base, Rate.quote == quote))
        .order_by(desc(Rate.date))
        .limit(1)
    )
    return db.execute(stmt).scalar_one_or_none()

def get_max_date(db: Session):
    return db.execute(select(func.max(Rate.date))).scalar()

def serialize_rates(rows: list[Rate]) -> list[dict]:
    return [
        {
            "date": r.date.isoformat(),
            "base": r.base,
            "quote": r.quote,
            "rate": r.rate,
            "source": r.source,
        }
        for r in rows
    ]
