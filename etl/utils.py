from datetime import date, timedelta

def daterange(start: date, end: date, step_days: int = 60):
    cur = start
    while cur <= end:
        to = min(cur + timedelta(days=step_days-1), end)
        yield cur, to
        cur = to + timedelta(days=1)
