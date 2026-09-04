import asyncio

from fastapi import APIRouter
from openai import AzureOpenAI
from sqlalchemy import text

from backend.config.logging_config import get_logger
from backend.config.settings import settings
from backend.database.session import SessionLocal

router = APIRouter(
    prefix="/health",
    tags=["Health"],
)

logger = get_logger(__name__)


# ---------------------------------------------------------
# Checks
# ---------------------------------------------------------

async def check_api_status() -> bool:
    """
    Basic application health.
    """

    return True


async def check_azure_openai() -> bool:
    """
    Lightweight Azure OpenAI validation.

    Lists available models, which validates
    credentials/connectivity without consuming
    completion or embedding tokens.
    """

    def _check() -> None:
        client = AzureOpenAI(
            api_key=settings.AZURE_OPENAI_API_KEY,
            api_version=settings.AZURE_OPENAI_API_VERSION,
            azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
        )

        client.models.list()

    try:
        await asyncio.to_thread(_check)
        return True

    except Exception:
        logger.exception("Azure OpenAI health check failed")
        return False


async def check_postgresql() -> bool:
    """
    Validates PostgreSQL connectivity with a trivial query.
    """

    def _check() -> None:
        with SessionLocal() as session:
            session.execute(text("SELECT 1"))

    try:
        await asyncio.to_thread(_check)
        return True

    except Exception:
        logger.exception("PostgreSQL health check failed")
        return False


# ---------------------------------------------------------
# Health Endpoint
# ---------------------------------------------------------

@router.get("")
async def health_check():
    """
    Platform readiness endpoint.
    """

    api_ok = await check_api_status()
    openai_ok = await check_azure_openai()
    postgres_ok = await check_postgresql()

    overall_status = (
        "healthy"
        if all([api_ok, openai_ok, postgres_ok])
        else "degraded"
    )

    return {
        "application": settings.PROJECT_NAME,
        "version": settings.PROJECT_VERSION,
        "environment": settings.ENVIRONMENT,
        "status": overall_status,
        "checks": {
            "api": api_ok,
            "azure_openai": openai_ok,
            "postgresql": postgres_ok,
        },
    }
