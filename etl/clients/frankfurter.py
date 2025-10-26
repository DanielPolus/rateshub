import httpx
from datetime import date

BASE_URL = "https://api.frankfurter.app"

async def fetch_range(base: str, quotes: list[str], start: date, end: date):
    syms = ",".join(quotes)
    url = f"{BASE_URL}/{start.isoformat()}..{end.isoformat()}?from={base}&to={syms}"
    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.get(url)
        r.raise_for_status()
        data = r.json()

    out = []
    rates_by_day = data.get("rates", {})
    for d_str, rates in rates_by_day.items():
        d = date.fromisoformat(d_str)
        for q, val in rates.items():
            out.append({"date": d, "base": base, "quote": q, "rate": float(val), "source": "frankfurter"})
    return out
