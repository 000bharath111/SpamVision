# app/db/session.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from ..config import settings

engine = create_engine(settings.DATABASE_URL, connect_args={"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {})
SessionLocal = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

def get_db_session():
    return SessionLocal()
