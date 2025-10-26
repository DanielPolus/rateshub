from __future__ import annotations
from datetime import date, timedelta

def parse_window(s: str) -> timedelta:
    s = s.strip().lower()
    if s.endswith("d"):
        return timedelta(days=int(s[:-1]))
    if s.endswith("w"):
        return timedelta(days=int(s[:-1]) * 7)
    if s.endswith("m"):
        return timedelta(days=int(s[:-1]) * 30)
    raise ValueError(f"Unsupported window: {s}")

def window_to_dates(window: str) -> tuple[date, date]:
    delta = parse_window(window)
    end = date.today()
    start = end - delta
    return start, end
