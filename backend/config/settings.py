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

    # --------------------------------------------------------
    # Logging
    # --------------------------------------------------------

    LOG_LEVEL: str = Field(default="INFO")

    # --------------------------------------------------------
    # Computed Properties
    # --------------------------------------------------------

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

