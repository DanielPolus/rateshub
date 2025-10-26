import sys, pathlib
sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))

import asyncio
from datetime import datetime, timezone

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

from etl.incremental import run_incremental_for_all_pairs


async def job():
    try:
        inserted = await run_incremental_for_all_pairs()
        print(f"[scheduler] {datetime.now().isoformat()} incremental ok, inserted={inserted}")
    except Exception as e:
        print(f"[scheduler] {datetime.now().isoformat()} incremental failed: {e}")


async def main():
    sched = AsyncIOScheduler(timezone="UTC")
    sched.add_job(
        job,
        IntervalTrigger(minutes=1),
        next_run_time=datetime.now(timezone.utc),
        id="incremental_every_minute",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
    )

    sched.start()
    print("[scheduler] started. Press Ctrl+C to exit.")

    stop_event = asyncio.Event()
    try:
        await stop_event.wait()
    except (KeyboardInterrupt, SystemExit):
        pass
    finally:
        sched.shutdown(wait=False)
        print("[scheduler] stopped.")


if __name__ == "__main__":
    asyncio.run(main())
