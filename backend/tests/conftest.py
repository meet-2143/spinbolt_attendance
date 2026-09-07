import os

os.environ.setdefault(
    "DATABASE_URL", "postgresql://attendance:attendance@localhost:5432/attendance_test"
)

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.auth.security import hash_password
from app.database.session import Base, get_db
from app.main import app
from app.models.user import User, UserRole, UserStatus

TEST_DATABASE_URL = os.environ["DATABASE_URL"]
# Set this when DATABASE_URL points at a real project database (e.g. Supabase)
# rather than a disposable local `attendance_test` database. Tests then run in
# their own Postgres schema and DROP it at teardown, instead of dropping every
# table in `public` - which could be real app/seed data on a shared instance.
TEST_DB_SCHEMA = os.environ.get("TEST_DB_SCHEMA")


@pytest.fixture(scope="session")
def db_engine():
    engine = create_engine(TEST_DATABASE_URL)

    if TEST_DB_SCHEMA:
        with engine.begin() as conn:
            conn.execute(text(f'CREATE SCHEMA IF NOT EXISTS "{TEST_DB_SCHEMA}"'))
        engine = engine.execution_options(schema_translate_map={None: TEST_DB_SCHEMA})

    Base.metadata.create_all(engine)
    yield engine

    if TEST_DB_SCHEMA:
        with engine.begin() as conn:
            conn.execute(text(f'DROP SCHEMA IF EXISTS "{TEST_DB_SCHEMA}" CASCADE'))
    else:
        Base.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture()
def db_session(db_engine):
    connection = db_engine.connect()
    transaction = connection.begin()
    # join_transaction_mode="create_savepoint" means session.commit() calls inside
    # the app/service layer only release a SAVEPOINT, not the outer transaction -
    # so rolling that back below fully undoes the test regardless of inner commits.
    SessionLocal = sessionmaker(
        autocommit=False, autoflush=False, bind=connection, join_transaction_mode="create_savepoint"
    )
    session = SessionLocal()

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture()
def client(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def make_user(db_session, *, role, status=UserStatus.ACTIVE, email=None, password="Password123!"):
    email = email or f"{role.value.lower()}@test.dev"
    user = User(
        name=f"Test {role.value.title()}",
        email=email,
        password_hash=hash_password(password),
        role=role,
        status=status,
    )
    db_session.add(user)
    db_session.flush()
    db_session.commit()
    return user


@pytest.fixture()
def admin_user(db_session):
    return make_user(db_session, role=UserRole.ADMIN, email="admin@test.dev")


@pytest.fixture()
def supervisor_user(db_session):
    return make_user(db_session, role=UserRole.SUPERVISOR, email="supervisor@test.dev")


@pytest.fixture()
def inactive_supervisor_user(db_session):
    return make_user(
        db_session,
        role=UserRole.SUPERVISOR,
        status=UserStatus.INACTIVE,
        email="inactive@test.dev",
    )


@pytest.fixture()
def second_supervisor_user(db_session):
    return make_user(db_session, role=UserRole.SUPERVISOR, email="supervisor2@test.dev")


def login_as(client, user, password="Password123!"):
    resp = client.post("/api/auth/login", json={"email": user.email, "password": password})
    assert resp.status_code == 200, resp.text
    return resp
