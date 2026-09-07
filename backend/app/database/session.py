from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker
from sqlalchemy.pool import NullPool

from app.config import get_settings

settings = get_settings()

# Serverless (Vercel) functions are stateless/short-lived, so pooling is delegated
# to Supabase's Supavisor (transaction-mode) pooler in front of DATABASE_URL rather
# than kept in-process. Locally, normal SQLAlchemy pooling against docker-compose
# Postgres is fine.
_engine_kwargs = {"pool_pre_ping": True}
if settings.is_serverless:
    _engine_kwargs["poolclass"] = NullPool

engine = create_engine(settings.database_url, **_engine_kwargs)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
