import os
from urllib.parse import quote_plus
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 1. Get raw password (including @ or other special characters)
RAW_PASSWORD = os.getenv("DB_PASSWORD", "Makdewyze1997@")

# 2. URL-encode password (@ becomes %40)
ENCODED_PASSWORD = quote_plus(RAW_PASSWORD)

# 3. Construct connection URL
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    f"postgresql+psycopg2://postgres:{ENCODED_PASSWORD}@127.0.0.1:5432/telecom_db"
)

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()