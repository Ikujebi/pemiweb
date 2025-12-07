from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")  # e.g. postgresql+psycopg2://user:pass@localhost:5432/webmail_db

# SQLAlchemy engine
engine = create_engine(DATABASE_URL, echo=True)

# SessionLocal class for creating DB sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for ORM models
Base = declarative_base()
