# tasks.py
import os
from celery import Celery
from dotenv import load_dotenv
from send_helpers import send_email_sendgrid, send_sms_twilio
from models import SessionLocal, SendLog, Recipient, Campaign
import datetime

load_dotenv()
CELERY_BROKER = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
CELERY_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/1")

celery = Celery("mail_tasks", broker=CELERY_BROKER, backend=CELERY_BACKEND)

@celery.task(bind=True, max_retries=3, default_retry_delay=30)
def send_to_recipient(self, sendlog_id):
    """
    Worker picks a send log row and tries to send via appropriate channel.
    """
    db = SessionLocal()
    try:
        sendlog = db.get(SendLog, sendlog_id)
        if not sendlog:
            return {"ok": False, "error": "log missing"}

        recipient = db.get(Recipient, sendlog.recipient_id)
        campaign = db.get(Campaign, sendlog.campaign_id)

        sendlog.attempt += 1
        sendlog.last_attempt_at = datetime.datetime.utcnow()
        db.add(sendlog)
        db.commit()

        if sendlog.channel == "email" and recipient.email:
            status, resp = send_email_sendgrid(recipient.email, campaign.subject or "", campaign.body or "")
            if 200 <= status < 300:
                sendlog.status = "success"
                db.add(sendlog); db.commit()
                return {"ok": True}
            else:
                raise Exception(f"email error {status}: {resp}")

        elif sendlog.channel == "sms" and recipient.phone:
            sid = send_sms_twilio(recipient.phone, campaign.body or "")
            sendlog.status = "success"
            db.add(sendlog); db.commit()
            return {"ok": True}
        else:
            sendlog.status = "failed"
            sendlog.error = "invalid channel or missing recipient contact"
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
    finally:
        db.close()
