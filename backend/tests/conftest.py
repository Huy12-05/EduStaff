"""
pytest conftest — redirects the app to an in-process SQLite database.

os.environ MUST be set before any app module is imported so that
pydantic-settings and SQLAlchemy pick up the values at module-load time.
"""
import os

os.environ.setdefault("DATABASE_URL", "sqlite:///./test_edustaff.db")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key-for-pytest-not-production")
os.environ.setdefault("APP_ENV", "dev")

import pytest
from fastapi.testclient import TestClient

import app.services.store as store_module
from app.db.base import Base
from app.db.session import engine, SessionLocal
from app.main import app

# SQLite needs check_same_thread=False for TestClient's thread model.
# Re-create the engine/session targeting the same SQLite file but with that flag.
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

_sqlite_engine = create_engine(
    os.environ["DATABASE_URL"],
    connect_args={"check_same_thread": False},
)
_TestSession = sessionmaker(bind=_sqlite_engine, autocommit=False, autoflush=False, expire_on_commit=False)

# Redirect the store to use the test session.
store_module.SessionLocal = _TestSession


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    Base.metadata.drop_all(bind=_sqlite_engine)
    Base.metadata.create_all(bind=_sqlite_engine)
    yield
    Base.metadata.drop_all(bind=_sqlite_engine)


@pytest.fixture(scope="session")
def client(setup_database):
    # Disable lifespan events (seed_initial_data would try MySQL).
    # We seed data manually in the fixture below.
    with TestClient(app, raise_server_exceptions=True) as c:
        yield c


@pytest.fixture(scope="session")
def seeded(client):
    """Seed one admin + one staff account and return their tokens."""
    from app.core.security import hash_password
    from app.models.entities import Account, Department, Lecturer
    from datetime import date

    with _TestSession() as db:
        if db.query(Account).count() == 0:
            db.add_all([
                Account(username="admin", full_name="Admin Test", role="admin",
                        is_active=True, password_hash=hash_password("admin123")),
                Account(username="staff1", full_name="Staff Test", role="staff",
                        is_active=True, password_hash=hash_password("staff123")),
            ])
            dep = Department(code="TEST", name="Khoa Test", description="Test dept")
            db.add(dep)
            db.flush()
            db.add(Lecturer(
                employee_code="GV_TEST01",
                full_name="Nguyen Test",
                email="test@eaut.edu.vn",
                phone="0900000001",
                gender="male",
                date_of_birth=date(1985, 1, 1),
                degree="ThS",
                position="Giang vien",
                department_id=dep.id,
                hire_date=date(2015, 9, 1),
                status="active",
            ))
            db.commit()

    admin_resp = client.post("/auth/token", data={"username": "admin", "password": "admin123"})
    staff_resp = client.post("/auth/token", data={"username": "staff1", "password": "staff123"})
    return {
        "admin_token": admin_resp.json()["access_token"],
        "staff_token": staff_resp.json()["access_token"],
    }
