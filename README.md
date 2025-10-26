# 💱 RatesHub — Currency Data ETL & Analytics Backend

A modern **FastAPI + PostgreSQL** backend for collecting, storing, and visualizing foreign exchange (FX) rates.  
Includes an **asynchronous ETL scheduler**, **data analytics API**, and a lightweight **HTML/Chart.js dashboard**.

---

## 🚀 Features

- **FastAPI backend**
  - `/rates`, `/analytics/summary`, `/metrics`, `/export`
- **ETL Scheduler**
  - Periodically fetches fresh FX rates from [Frankfurter API](https://www.frankfurter.app)
  - Saves updates to PostgreSQL via async SQLAlchemy
- **Database**
  - PostgreSQL + Alembic migrations
  - Dockerized setup (`docker-compose up -d`)
- **Dashboard**
  - Live visualization of EUR/USD, GBP, PLN, RON etc.
  - Real-time ETL status indicator (🟢 Healthy / 🔴 Stale)
  - Data export to **CSV** or **Parquet**
- **Analytics**
  - Average, min/max, standard deviation, change%
  - Rolling windows (`last=7d`, `last=30d`, etc.)

---

## 🧱 Tech Stack

**Backend**
- FastAPI (REST API)
- SQLAlchemy + Alembic (ORM & migrations)
- PostgreSQL (Dockerized)
- APScheduler (background ETL)
- Pydantic v2
- Pandas / PyArrow (data export)

**Frontend**
- Jinja2 templates
- Chart.js for visualization
- Pure CSS dark theme

---

## ⚙️ Local Setup

### 1️⃣ Clone the repo
```
git clone https://github.com/<your-username>/rateshub
cd rateshub
```

### 2️⃣ Create .env
```
DATABASE_URL=postgresql+psycopg2://rates:rates@localhost:5433/rateshub
```

### 3️⃣ Start PostgreSQL
```
docker compose up -d
```

### 4️⃣ Run migrations
```
alembic upgrade head
```

### 5️⃣ Seed currency symbols
```
python -m seeds.seed_symbols
```

### 6️⃣ Start the API
```
uvicorn app.main:app --reload
```

### 7️⃣ Start the ETL Scheduler (optional)
```
python etl/scheduler.py
```

Then open 
```
http://127.0.0.1:8000/dashboard
```

If you read it, you must know that I'm a cat person.
