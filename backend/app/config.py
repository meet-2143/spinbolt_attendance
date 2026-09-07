from functools import lru_cache
from zoneinfo import ZoneInfo

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Runtime app connection string used at request time (pooled, in prod).
    database_url: str = "postgresql://attendance:attendance@localhost:5432/attendance"
    # Direct (non-pooled) connection string used only for running Alembic migrations.
    database_url_direct: str | None = None

    jwt_secret: str = "dev-secret-change-me"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60 * 12

    app_timezone: str = "Asia/Kolkata"

    environment: str = "development"

    cors_origins: str = "http://localhost:5173"

    @property
    def tzinfo(self) -> ZoneInfo:
        return ZoneInfo(self.app_timezone)

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def is_serverless(self) -> bool:
        return self.environment == "production"


@lru_cache
def get_settings() -> Settings:
    return Settings()
