from fastapi import APIRouter

from backend.config.settings import settings

router = APIRouter(
    prefix="/health",
    tags=["Health"],
)


# ---------------------------------------------------------
# Placeholder Checks
# ---------------------------------------------------------

async def check_api_status() -> bool:
    """
    Basic application health.
    """

    return True


async def check_azure_openai() -> bool:
    """
    Placeholder for Azure OpenAI validation.

    Milestone 1:
    Returns True.

    Future:
    Perform lightweight API validation.
    """

    return True


async def check_postgresql() -> bool:
    """
    Placeholder for PostgreSQL validation.

    Milestone 1:
    Returns True.

    Future:
    Execute SELECT 1.
    """

    return True


# ---------------------------------------------------------
# Health Endpoint
# ---------------------------------------------------------

@router.get("")
async def health_check():
    """
    Platform readiness endpoint.

    Future integrations:
    - PostgreSQL
    - Azure OpenAI
    - Blob Storage
    - Key Vault
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