# models.py
import os
import datetime
from dotenv import load_dotenv
from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, ForeignKey, Text, create_engine
)
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

# Load environment variables from .env
load_dotenv()
# Use DATABASE_URL from .env; fallback to local SQLite for testing
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///mailing.db")

# Base class for models
Base = declarative_base()

# -------------------------
# Database Models
# -------------------------

class Recipient(Base):
    __tablename__ = "recipients"
    id = Column(Integer, primary_key=True)
    email = Column(String(320), nullable=True, index=True)  # max email length
    phone = Column(String(32), nullable=True, index=True)
    opted_in = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    send_logs = relationship("SendLog", back_populates="recipient")


class Campaign(Base):
    __tablename__ = "campaigns"
    id = Column(Integer, primary_key=True)
    name = Column(String(200))
    subject = Column(String(300), nullable=True)
    body = Column(Text)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    send_logs = relationship("SendLog", back_populates="campaign")


class SendLog(Base):
    __tablename__ = "send_logs"
    id = Column(Integer, primary_key=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"))
    recipient_id = Column(Integer, ForeignKey("recipients.id"))
    channel = Column(String(10))  # "email" or "sms"
    status = Column(String(20))   # pending, success, failed
    error = Column(Text, nullable=True)
    attempt = Column(Integer, default=0)
    last_attempt_at = Column(DateTime, default=None)

    # Relationships
    campaign = relationship("Campaign", back_populates="send_logs")
    recipient = relationship("Recipient", back_populates="send_logs")

# -------------------------
# Engine & Session
# -------------------------
engine = create_engine(DATABASE_URL, echo=True, future=True)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)

# -------------------------
# Initialize DB (create tables)
# -------------------------
def init_db():
    """Creates all tables in the database."""
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")
