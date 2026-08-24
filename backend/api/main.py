from contextlib import asynccontextmanager
from time import perf_counter

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import Response

from backend.api.routers.health import router as health_router

from backend.api.routers.embedding import (
    router as embedding_router,
)

from backend.api.routers.search import (
    router as search_router,
)

from backend.config.logging_config import (
    configure_logging,
    get_logger,
)
from backend.config.settings import settings

from backend.api.routers.catalog import (
    router as catalog_router,
)

from backend.api.routers.generation import (
    router as generation_router,
)

from backend.api.routers.publish import (
    router as publish_router,
)


# ---------------------------------------------------------
# Logging
# ---------------------------------------------------------

configure_logging(settings.LOG_LEVEL)
logger = get_logger(__name__)


# ---------------------------------------------------------
# Lifespan Management
# ---------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application startup and shutdown lifecycle.

    This is the correct place for:
    - Database initialization
    - Connection pool setup
    - Cache initialization
    - Azure client initialization
    """

    logger.info(
        "Starting ANS API",
        extra={
            "environment": settings.ENVIRONMENT,
            "version": settings.PROJECT_VERSION,
        },
    )

    try:
        yield

    finally:
        logger.info("Shutting down ANS API")


# ---------------------------------------------------------
# FastAPI App
# ---------------------------------------------------------

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)


# ---------------------------------------------------------
# CORS Configuration
# ---------------------------------------------------------

ALLOWED_ORIGINS = [
    "http://localhost:8501",  # Streamlit local development
]

if settings.ENVIRONMENT.lower() != "prod":
    ALLOWED_ORIGINS.append("http://127.0.0.1:8501")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


# ---------------------------------------------------------
# Request Logging Middleware
# ---------------------------------------------------------

@app.middleware("http")
async def log_requests(
    request: Request,
    call_next,
) -> Response:
    """
    Logs every incoming request and response.

    Azure Application Insights can ingest
    structured logs generated here.
    """

    start_time = perf_counter()

    logger.info(
        f"Request Started | "
        f"Method={request.method} "
        f"Path={request.url.path}"
    )

    try:

        response = await call_next(request)

        process_time = round(
            (perf_counter() - start_time) * 1000,
            2,
        )

        logger.info(
            f"Request Completed | "
            f"Method={request.method} "
            f"Path={request.url.path} "
            f"Status={response.status_code} "
            f"DurationMs={process_time}"
        )

        response.headers["X-Process-Time-MS"] = str(
            process_time
        )

        return response

    except Exception as ex:

        logger.exception(
            f"Unhandled Exception | "
            f"Method={request.method} "
            f"Path={request.url.path} "
            f"Error={str(ex)}"
        )

        raise


# ---------------------------------------------------------
# Routers
# ---------------------------------------------------------

app.include_router(
    health_router,
    tags=["Health"],
)

app.include_router(
    embedding_router,
    tags=["Embeddings"],
)

app.include_router(
    search_router,
    tags=["Search"],
)

app.include_router(
    catalog_router,
)

app.include_router(
    generation_router,
    tags=["Generation"],
)

app.include_router(
    publish_router
)
# ---------------------------------------------------------
# Root Endpoint
# ---------------------------------------------------------

@app.get("/", tags=["System"])
async def root():
    """
    Root endpoint.

    Useful for quick checks that
    the application is running.
    """

    return {
        "application": settings.PROJECT_NAME,
        "version": settings.PROJECT_VERSION,
        "environment": settings.ENVIRONMENT,
        "status": "running",
    }