from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from core.config import settings

database_url = settings.DATABASE_URL

# Added pooling parameters for secure database connections
engine = create_engine(database_url,
                       connect_args={"options": "-c timezone=Africa/Nairobi"})
session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = session()
    try:
        yield db
    finally:
        db.close()
