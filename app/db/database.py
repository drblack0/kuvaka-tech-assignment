from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

# Singleton variables
_engine = None
_Session = None


def get_engine():
    global _engine
    if _engine is None:
        DATABASE_URL = "postgresql+psycopg2://postgres:0000@localhost:5432/postgres"
        _engine = create_engine(DATABASE_URL, pool_pre_ping=True, future=True)
    return _engine


def get_session():
    global _Session
    if _Session is None:
        engine = get_engine()
        # scoped_session ensures thread-safety in Flask
        _Session = scoped_session(
            sessionmaker(bind=engine, autoflush=False, autocommit=False)
        )
    return _Session
