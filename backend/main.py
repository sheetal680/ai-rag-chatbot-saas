from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import router as v1_router
from app.core.config import settings
from app.core.logging import setup_logging
from app.db.postgres import connect_db, disconnect_db, ensure_tables, get_pool
from app.middleware.request_logging import RequestLoggingMiddleware

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging(environment=settings.ENVIRONMENT, log_level=settings.LOG_LEVEL)
    logger.info("startup", environment=settings.ENVIRONMENT, version=settings.APP_VERSION)
    try:
        await connect_db()
        await ensure_tables()
        logger.info("startup.db_ready")
    except Exception as exc:
        logger.warning("startup.db_unavailable", error=str(exc))
    yield
    await disconnect_db()
    logger.info("shutdown")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    # Swagger UI is hidden in production — no API surface exposed to the public
    docs_url=settings.docs_url,
    redoc_url=settings.redoc_url,
    lifespan=lifespan,
)

app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(v1_router, prefix="/api/v1")


@app.get("/health", tags=["Monitoring"])
async def health_check() -> dict:
    """Liveness probe — returns 200 as long as the process is running."""
    return {"status": "ok", "version": settings.APP_VERSION, "env": settings.ENVIRONMENT}


@app.get("/health/ready", tags=["Monitoring"])
async def readiness_check() -> dict:
    """Readiness probe — also verifies the database connection."""
    db_status = "ok"
    try:
        pool = get_pool()
        await pool.fetchval("SELECT 1")
    except Exception:
        db_status = "error"

    status = "ok" if db_status == "ok" else "degraded"
    return {"status": status, "version": settings.APP_VERSION, "db": db_status}
