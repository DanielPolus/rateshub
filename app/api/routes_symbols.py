from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.db import SessionLocal
from app.schemas.symbol import SymbolOut
from app.services.symbols_service import list_symbols

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/", response_model=list[SymbolOut])
def symbols(db: Session = Depends(get_db)):
    return list_symbols(db)
