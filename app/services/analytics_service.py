from datetime import date
from sqlalchemy import select, func, and_, asc
from sqlalchemy.orm import Session
from app.models.rate import Rate

def analytics_summary(
        db: Session,
        base: str,
        quote: str,
        start: date,
        end: date,
) -> dict:
    cond = and_(
        Rate.base == base,
        Rate.quote == quote,
        Rate.date >= start,
        Rate.date <= end,
    )

    agg_stmt = select(
        func.count().label("count"),
        func.min(Rate.rate).label("min"),
        func.max(Rate.rate).label("max"),
        func.avg(Rate.rate).label("avg"),
        func.stddev_samp(Rate.rate).label("stddev")
    ).where(cond)
    agg = db.execute(agg_stmt).mappings().one()
    count = int(agg["count"])

    first_stmt = (
        select(Rate.rate)
        .where(cond)
        .order_by(asc(Rate.date))
        .limit(1)
    )
    last_stmt = (
        select(Rate.rate)
        .where(cond)
        .order_by(Rate.date.desc())
        .limit(1)
    )
    first_row = db.execute(first_stmt).scalar_one_or_none()
    last_row = db.execute(last_stmt).scalar_one_or_none()

    change_abs = None
    change_pct = None
    if first_row is not None and last_row is not None:
        change_abs = float(last_row - first_row)
        if first_row != 0:
            change_pct = float((last_row - first_row) - 1.0)

    return {
        "base": base,
        "quote": quote,
        "start": start.isoformat(),
        "end": end.isoformat(),
        "count": count,
        "min": float(agg["min"]) if agg["min"] is not None else None,
        "max": float(agg["max"]) if agg["max"] is not None else None,
        "avg": float(agg["avg"]) if agg["avg"] is not None else None,
        "stddev": float(agg["stddev"]) if agg["stddev"] is not None else None,
        "first_row": float(first_row) if first_row is not None else None,
        "last_row": float(last_row) if last_row is not None else None,
        "change_abs": change_abs,
        "change_pct": change_pct,
    }
