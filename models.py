import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from database import Base  # Make sure database.py defines Base = declarative_base()

class Recipient(Base):
    __tablename__ = "recipients"

    id = Column(Integer, primary_key=True)
    email = Column(String(320), index=True, nullable=True)
    phone = Column(String(32), index=True, nullable=True)
    opted_in = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationship to SendLog
    send_logs = relationship("SendLog", back_populates="recipient")


class Campaign(Base):
    __tablename__ = "campaigns"

    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    subject = Column(String(300), nullable=True)
    body = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationship to SendLog
    send_logs = relationship("SendLog", back_populates="campaign")


class SendLog(Base):
    __tablename__ = "send_logs"

    id = Column(Integer, primary_key=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"))
    recipient_id = Column(Integer, ForeignKey("recipients.id"))
    channel = Column(String(10))          # "email" or "sms"
    status = Column(String(20))           # pending, success, failed
    error = Column(Text, nullable=True)
    attempt = Column(Integer, default=0)
    last_attempt_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    campaign = relationship("Campaign", back_populates="send_logs")
    recipient = relationship("Recipient", back_populates="send_logs")
