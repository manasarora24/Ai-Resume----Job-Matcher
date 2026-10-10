from sqlalchemy import create_engine, event
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy.pool import StaticPool
from .config import settings

connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
engine_options = {"poolclass": StaticPool} if settings.database_url in {"sqlite://", "sqlite:///:memory:"} else {}
engine = create_engine(settings.database_url, connect_args=connect_args, pool_pre_ping=True, **engine_options)
if settings.database_url.startswith("sqlite"):
    @event.listens_for(engine, "connect")
    def enable_sqlite_foreign_keys(connection, _record):
        cursor = connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)

class Base(DeclarativeBase):
    pass

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
