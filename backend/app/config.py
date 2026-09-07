from functools import lru_cache
from zoneinfo import ZoneInfo

from pydantic_settings import BaseSettings, SettingsConfigDict


def normalize_db_url(url: str) -> str:
    """Force the psycopg3 driver explicitly, so a plain "postgresql://" URL
    (e.g. copied straight from Supabase's dashboard) works without the caller
    needing to know about SQLAlchemy dialect prefixes - SQLAlchemy otherwise
    defaults bare "postgresql://" URLs to the psycopg2 driver."""
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+psycopg://", 1)
    return url


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
    def database_url_normalized(self) -> str:
        return normalize_db_url(self.database_url)

    @property
    def database_url_direct_normalized(self) -> str | None:
        return normalize_db_url(self.database_url_direct) if self.database_url_direct else None

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
