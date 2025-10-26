import sys, pathlib; sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))
import asyncio
from datetime import date
from app.core.config import settings
from app.core.db import session_scope
from app.models.rate import Rate
from etl.clients.frankfurter import fetch_range
from etl.validators import validate_batch

async def run_backfill(base="EUR", quotes=("USD","GBP","PLN","RON")):
    rows = await fetch_range(
        base=base,
        quotes=list(quotes),
        start=date.fromisoformat(settings.ETL_BACKFILL_START),
        end=date.today()
    )
    validate_batch(rows)
    with session_scope() as s:
        for r in rows:
            s.merge(Rate(**r))

if __name__ == "__main__":
    asyncio.run(run_backfill())
