import os

# backend.config.settings.Settings() is instantiated eagerly at module
# import time (backend/config/settings.py: `settings = get_settings()`),
# and anything importing the database session chain (repositories,
# backend.data.pipeline) pulls that in transitively. Without a real
# .env, that import fails before a single test runs. setdefault() only
# fills gaps, so a real .env/real env vars for local DB work still win.
os.environ.setdefault("PROJECT_NAME", "ANS Test")
os.environ.setdefault("PROJECT_VERSION", "0.0.0-test")
os.environ.setdefault("ENVIRONMENT", "test")
os.environ.setdefault("API_HOST", "0.0.0.0")
os.environ.setdefault("API_PORT", "8000")
os.environ.setdefault("API_PREFIX", "/api")
os.environ.setdefault("POSTGRES_HOST", "localhost")
os.environ.setdefault("POSTGRES_PORT", "5432")
os.environ.setdefault("POSTGRES_USER", "test")
os.environ.setdefault("POSTGRES_PASSWORD", "test")
os.environ.setdefault("POSTGRES_DB", "test")
os.environ.setdefault("AZURE_OPENAI_API_KEY", "test")
os.environ.setdefault("AZURE_OPENAI_ENDPOINT", "https://example.invalid")
os.environ.setdefault("AZURE_OPENAI_API_VERSION", "2024-01-01")
os.environ.setdefault("AZURE_OPENAI_EMBEDDING_DEPLOYMENT", "test")
os.environ.setdefault("AZURE_OPENAI_CHAT_DEPLOYMENT", "test")
os.environ.setdefault("AZURE_OPENAI_CLASSIFICATION_DEPLOYMENT", "test")
