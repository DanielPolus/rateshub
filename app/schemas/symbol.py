from pydantic import BaseModel
from typing import Optional

class SymbolOut(BaseModel):
    code: str
    name: Optional[str] = None

    class Config:
        from_attributes = True
