from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings


engine = create_engine(
	settings.database_url,
	pool_pre_ping=True,
	pool_recycle=3600,
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
