from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.db import SessionLocal
from app.core.config import settings
from app.services.rates_service import get_max_date

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/", tags=["health"])
def health(db: Session = Depends(get_db)):
    max_date = get_max_date(db)
    return {
        "app": settings.APP_NAME,
        "status": "ok",
        "data_fresh_until": str(max_date) if max_date else None,
    }
