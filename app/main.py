from fastapi import FastAPI
from app.api.routes_health import router as health_router
from app.api.routes_symbols import router as symbols_router
from app.api.routes_rates import router as rates_router
from app.api.routes_analytics import router as analytics_router
from app.api.routes_metrics import router as metrics_router
from app.core.logging import setup_logging
from app.ui.routes_dashboard import router as dashboard_router
from fastapi.staticfiles import StaticFiles
from app.api.routes_export import router as export_router

def get_app():
    setup_logging()
    app = FastAPI(title="RatesHub")
    app.include_router(health_router,   prefix="/health")
    app.include_router(symbols_router,  prefix="/symbols")
    app.include_router(rates_router,    prefix="/rates")
    app.include_router(analytics_router, prefix="/analytics")
    app.include_router(metrics_router,  prefix="/metrics")
    app.include_router(export_router, prefix="/export", tags=["export"])
    app.include_router(dashboard_router)

    app.mount("/static", StaticFiles(directory="static"), name="static")

    return app

app = get_app()
