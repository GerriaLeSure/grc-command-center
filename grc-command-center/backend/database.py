from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import settings

# PostgreSQL setup
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """Dependency for getting database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# MongoDB setup (alternative)
from pymongo import MongoClient

mongo_client = None

def get_mongo_db():
    """Get MongoDB database"""
    global mongo_client
    if mongo_client is None:
        mongo_client = MongoClient(settings.MONGODB_URL)
    return mongo_client[settings.MONGODB_DB]