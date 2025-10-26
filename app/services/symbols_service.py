from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.symbol import Symbol

def list_symbols(db: Session):
    return db.execute(select(Symbol)).scalars().all()
