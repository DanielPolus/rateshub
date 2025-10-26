from app.core.db import session_scope
from app.models.symbol import Symbol

SYMBOLS = [
    ("EUR", "Euro"),
    ("USD", "US Dollar"),
    ("GBP", "British Pound"),
    ("PLN", "Polish Zloty"),
    ("RON", "Romanian Leu"),
]

if __name__ == "__main__":
    with session_scope() as s:
        for code, name in SYMBOLS:
            if not s.get(Symbol, code):
                s.add(Symbol(code=code, name=name))
