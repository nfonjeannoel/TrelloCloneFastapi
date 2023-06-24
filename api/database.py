from sqlalchemy import create_engine as _create_engine
from sqlalchemy.orm import sessionmaker as _sessionmaker
from sqlalchemy.ext.declarative import declarative_base as _declarative_base

DATABASE_URL = "sqlite:///./db.db"

engine = _create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

SessionLocal = _sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = _declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_db():
    Base.metadata.create_all(bind=engine)

