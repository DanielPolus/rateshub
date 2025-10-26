import sys, pathlib
sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))

import asyncio
from datetime import date, timedelta

from sqlalchemy import select, func
from app.core.db import session_scope, SessionLocal
from app.core.config import settings
from app.core.cache import cache_delete_pattern
from app.models.rate import Rate
from app.models.etl_run import ETLRun
from etl.clients.frankfurter import fetch_range
from etl.validators import validate_batch
from sqlalchemy.dialects.postgresql import insert

PAIRS = [
    ("EUR", "USD"),
    ("EUR", "GBP"),
    ("EUR", "PLN"),
    ("EUR", "RON"),
]

async def _sync_pair(base: str, quote: str) -> int:
    with session_scope() as s:
        max_date = s.execute(
            select(func.max(Rate.date)).where(Rate.base == base, Rate.quote == quote)
        ).scalar()

    start = (max_date + timedelta(days=1)) if max_date else date.fromisoformat(settings.ETL_BACKFILL_START)
    end = date.today()

    if start > end:
        return 0

    rows = await fetch_range(base=base, quotes=[quote], start=start, end=end)
    validate_batch(rows)
    inserted = 0

    with session_scope() as s:
        run = ETLRun(job="incremental", status="started")
        s.add(run);
        s.flush()

        if rows:
            stmt = insert(Rate).values(rows).on_conflict_do_update(
                index_elements=["date", "base", "quote", "source"],
                set_={
                    "rate": insert(Rate).excluded.rate,
                    "source": insert(Rate).excluded.source,
                },
            )
            result = s.execute(stmt)
            inserted = len(rows)

        run.status = "ok"
        run.rows_ingested = inserted

        if inserted > 0:
            deleted = cache_delete_pattern(f"rates:{base}:{quote}:*")
        return inserted


async def run_incremental_for_all_pairs() -> int:
    total = 0
    for base, quote in PAIRS:
        total += await _sync_pair(base, quote)
    return total

if __name__ == "__main__":
    inserted = asyncio.run(run_incremental_for_all_pairs())
    print(f"incremental done, inserted={inserted}")
