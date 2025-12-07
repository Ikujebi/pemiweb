# tasks.py
import os
import datetime
from celery import Celery
from dotenv import load_dotenv

from database import SessionLocal
from models import SendLog, Recipient, Campaign
from send_helpers import send_email_sendgrid, send_sms_twilio

load_dotenv()

CELERY_BROKER = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
CELERY_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/1")

celery = Celery("mail_tasks", broker=CELERY_BROKER, backend=CELERY_BACKEND)

@celery.task(bind=True, max_retries=3, default_retry_delay=30)
def send_to_recipient(self, sendlog_id: int):
    with SessionLocal() as db:
        try:
            sendlog = db.get(SendLog, sendlog_id)
            if not sendlog:
                return {"ok": False, "error": "sendlog not found"}

            recipient = db.get(Recipient, sendlog.recipient_id)
            campaign = db.get(Campaign, sendlog.campaign_id)

            sendlog.attempt += 1
            sendlog.last_attempt_at = datetime.datetime.utcnow()
            db.add(sendlog)
            db.commit()

            if sendlog.channel == "email" and recipient and recipient.email:
                status, resp = send_email_sendgrid(recipient.email, campaign.subject or "", campaign.body or "")
                if 200 <= status < 300:
                    sendlog.status = "success"
                    db.add(sendlog); db.commit()
                    return {"ok": True}
                raise Exception(f"SendGrid error {status}: {resp}")

            if sendlog.channel == "sms" and recipient and recipient.phone:
                send_sms_twilio(recipient.phone, campaign.body or "")
                sendlog.status = "success"
                db.add(sendlog); db.commit()
                return {"ok": True}

            sendlog.status = "failed"
            sendlog.error = "missing recipient contact or invalid channel"
            db.add(sendlog); db.commit()
            return {"ok": False, "error": sendlog.error}

        except Exception as exc:
            try:
                self.retry(exc=exc)
            except self.MaxRetriesExceededError:
                sendlog.status = "failed"
                sendlog.error = str(exc)
                db.add(sendlog); db.commit()
                return {"ok": False, "error": str(exc)}
