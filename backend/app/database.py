from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, declarative_base
from backend.app.config import settings

DATABASE_URL = settings.DATABASE_URL

if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        echo=settings.DATABASE_ECHO,
    )

    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()
else:
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20,
        echo=settings.DATABASE_ECHO,
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    from backend.app.models import (
        User, Dataset, DatasetMetadata, Prediction, ModelVersion,
        EnvironmentalMetric, CircularityMetric, SustainabilityScore,
        Report, AuditLog,
    )
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        if not db.query(User).first():
            from backend.app.utils.security import hash_password
            default_user = User(
                username="admin",
                email="admin@lca-platform.local",
                hashed_password=hash_password("admin123"),
                full_name="Admin",
                role="admin",
                is_active=True,
            )
            db.add(default_user)
            db.commit()
    finally:
        db.close()
