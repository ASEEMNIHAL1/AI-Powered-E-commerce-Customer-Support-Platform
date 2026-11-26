"""Application configuration loaded from environment variables."""
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Database
    database_url: str = "postgresql://acs_user:acs_secret@localhost:5432/acs_db"

    # JWT
    secret_key: str = "CHANGE_ME_IN_PRODUCTION_long_random_string"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    # AI
    ai_mock_mode: bool = True
    gemini_api_key: str = ""

    # CORS
    cors_origins: str = "http://localhost:5173,http://localhost:3000"

    # Business rules – stored server-side only, never from frontend
    refund_escalation_threshold: int = 500000  # paise (₹5000)

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",")]


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
