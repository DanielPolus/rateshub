from datetime import date

def validate_batch(rows: list[dict]):
    prev = None
    for r in rows:
        assert isinstance(r["date"], date), "date must be datetime.date"
        if r["rate"] <= 0:
            raise ValueError("rate must be positive")
        prev = r["rate"]
