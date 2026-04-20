from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings


engine = create_engine(
    settings.database_url,
    pool_pre_ping=False,      # local DB — no need to ping before every checkout
    pool_size=20,             # keep 20 persistent connections
    max_overflow=10,          # allow 10 extra under burst
    pool_recycle=1800,        # recycle every 30 min to avoid stale connections
    pool_timeout=10,
    connect_args={"connect_timeout": 5},
)

SessionLocal = sessionmaker(
	bind=engine,
	autocommit=False,
	autoflush=False,
	expire_on_commit=False,
)


def get_db() -> Generator[Session, None, None]:
	db = SessionLocal()
	try:
		yield db
	finally:
		db.close()


def init_db() -> None:
	# Import trong ham de tranh vong lap import khi startup.
	from app.db.base import Base
	from app.models import entities  # noqa: F401

	Base.metadata.create_all(bind=engine)
