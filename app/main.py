from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.logging import configure_logging, get_logger
from app.db.session import create_db_and_tables


@asynccontextmanager
async def lifespan(_: FastAPI):
    configure_logging(settings.LOG_LEVEL)
    logger = get_logger(__name__)
    logger.info("starting application", extra={"env": settings.APP_ENV})
    create_db_and_tables()
    yield
    logger.info("shutting down application")


app = FastAPI(
    title=settings.APP_NAME,
    docs_url="/docs" if settings.ENABLE_DOCS else None,
    redoc_url="/redoc" if settings.ENABLE_DOCS else None,
    openapi_url="/openapi.json" if settings.ENABLE_DOCS else None,
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allow_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

app.include_router(api_router, prefix=settings.API_V1_PREFIX)

if settings.ENABLE_STATIC_INDEX:
    app.mount("/static", StaticFiles(directory=str(settings.STATIC_DIR)), name="static")


@app.get("/", summary="Root")
def root():
    index_path = settings.STATIC_DIR / "index.html"
    if index_path.exists():
        return FileResponse(index_path)
    return {
        "message": f"{settings.APP_NAME} is running",
        "environment": settings.APP_ENV,
        "docs": "/docs",
        "health": f"{settings.API_V1_PREFIX}/health",
    }
