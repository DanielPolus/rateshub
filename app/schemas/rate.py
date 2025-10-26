from datetime import date
from pydantic import BaseModel

class RateOut(BaseModel):
    date: date
    base: str
    quote: str
    rate: float
    source: str

    class Config:
        from_attributes = True
