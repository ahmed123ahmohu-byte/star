# backend/config.py
# إعدادات التطبيق باستخدام Pydantic Settings

from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # General
    APP_NAME: str = "AI Assistant"
    DEBUG: bool = False
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # CORS
    BACKEND_CORS_ORIGINS: list = ["http://localhost", "http://localhost:8080"]

    # Database / Redis
    REDIS_URL: str = "redis://redis:6379/0"

    # GitHub OAuth
    GITHUB_CLIENT_ID: str
    GITHUB_CLIENT_SECRET: str
    GITHUB_REDIRECT_URI: str = "http://localhost:8000/api/auth/github/callback"

    # Joplin API
    JOPLIN_API_URL: str = "http://localhost:41184"  # افتراضي
    JOPLIN_TOKEN: str = ""

    # LLM API (مثال: OpenAI)
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4"

    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings():
    return Settings()
