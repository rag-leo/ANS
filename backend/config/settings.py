# ============================================================
# File: backend/config/settings.py
# ============================================================

from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from urllib.parse import quote_plus

class Settings(BaseSettings):
    """
    Centralized application configuration.

    Configuration priority:
    1. Environment Variables (Azure App Service / Container Apps)
    2. Local .env file
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

    # --------------------------------------------------------
    # Project Metadata
    # --------------------------------------------------------

    PROJECT_NAME: str = Field(...)
    PROJECT_VERSION: str = Field(...)
    ENVIRONMENT: str = Field(...)

    # --------------------------------------------------------
    # FastAPI
    # --------------------------------------------------------

    API_HOST: str = Field(...)
    API_PORT: int = Field(...)
    API_PREFIX: str = Field(...)

    # --------------------------------------------------------
    # PostgreSQL
    # --------------------------------------------------------

    POSTGRES_HOST: str = Field(...)
    POSTGRES_PORT: int = Field(...)
    POSTGRES_USER: str = Field(...)
    POSTGRES_PASSWORD: str = Field(...)
    POSTGRES_DB: str = Field(...)
    POSTGRES_SSLMODE: str = Field(default="require")

    # --------------------------------------------------------
    # Azure OpenAI
    # --------------------------------------------------------

    AZURE_OPENAI_API_KEY: str = Field(...)
    AZURE_OPENAI_ENDPOINT: str = Field(...)
    AZURE_OPENAI_API_VERSION: str = Field(...)

    AZURE_OPENAI_EMBEDDING_DEPLOYMENT: str = Field(...)
    AZURE_OPENAI_CHAT_DEPLOYMENT: str = Field(...)

    # Separate, deliberately cheaper deployment (e.g. gpt-4o-mini) used
    # only for ingestion-time crop/category classification — kept
    # distinct from AZURE_OPENAI_CHAT_DEPLOYMENT so a stronger/pricier
    # model used for content generation doesn't also get used, at
    # per-article volume, for a much simpler classification task.
    AZURE_OPENAI_CLASSIFICATION_DEPLOYMENT: str = Field(...)

    # --------------------------------------------------------
    # Logging
    # --------------------------------------------------------

    LOG_LEVEL: str = Field(default="INFO")

    # --------------------------------------------------------
    # CORS
    # --------------------------------------------------------

    # Comma-separated list of origins allowed to call this API.
    ALLOWED_ORIGINS: str = Field(
        default="http://localhost:8501,http://127.0.0.1:8501"
    )

    # --------------------------------------------------------
    # Computed Properties
    # --------------------------------------------------------

    @property
    def allowed_origins_list(self) -> list[str]:
        """
        ALLOWED_ORIGINS as a list, for CORSMiddleware.
        """

        return [
            origin.strip()
            for origin in self.ALLOWED_ORIGINS.split(",")
            if origin.strip()
        ]

    @property
    def database_url(self) -> str:
        """
        SQLAlchemy connection string
        """

        encoded_password = quote_plus(
            self.POSTGRES_PASSWORD
        )

        return (
            f"postgresql+psycopg2://"
            f"{self.POSTGRES_USER}:"
            f"{encoded_password}@"
            f"{self.POSTGRES_HOST}:"
            f"{self.POSTGRES_PORT}/"
            f"{self.POSTGRES_DB}"
            f"?sslmode={self.POSTGRES_SSLMODE}"
        )

@lru_cache
def get_settings() -> Settings:
    """
    Cached singleton settings instance.
    Prevents repeated .env parsing.
    """
    return Settings()


settings = get_settings()

