# models.py
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, ForeignKey, Text, create_engine
)
from sqlalchemy.orm import sessionmaker
import datetime
import os
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///mailing.db")

Base = declarative_base()

class Recipient(Base):
    __tablename__ = "recipients"
    id = Column(Integer, primary_key=True)
    email = Column(String(320), nullable=True, index=True)  # max email length
    phone = Column(String(32), nullable=True, index=True)
    opted_in = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class Campaign(Base):
    __tablename__ = "campaigns"
    id = Column(Integer, primary_key=True)
    name = Column(String(200))
    body = Column(Text)
    subject = Column(String(300), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

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

# Create engine and session factory
engine = create_engine(DATABASE_URL, echo=False, future=True)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)

def init_db():
    Base.metadata.create_all(bind=engine)
