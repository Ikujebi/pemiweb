# tasks.py
import os
import datetime
from celery import Celery
from dotenv import load_dotenv
from database import SessionLocal
from models import SendLog, Recipient, Campaign
from send_helpers import send_email_sendgrid, send_sms_twilio

load_dotenv()

# Celery config
CELERY_BROKER = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
CELERY_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/1")

celery = Celery("mail_tasks", broker=CELERY_BROKER, backend=CELERY_BACKEND)


@celery.task(bind=True, max_retries=3, default_retry_delay=30)
def send_to_recipient(self, sendlog_id: int):
    """
    Celery task to send a message (email or SMS) for a given SendLog ID.
    Updates SendLog status after sending.
    """
    try:
        # Open a fresh DB session
        with SessionLocal() as db:
            # Fetch the SendLog entry
            sendlog = db.get(SendLog, sendlog_id)
            if not sendlog:
                print(f"[send_to_recipient] SendLog {sendlog_id} not found")
                return {"ok": False, "error": "SendLog not found"}

            # Fetch related recipient and campaign
            recipient = db.get(Recipient, sendlog.recipient_id)
            campaign = db.get(Campaign, sendlog.campaign_id)

            # Update attempt info
            sendlog.attempt += 1
            sendlog.last_attempt_at = datetime.datetime.utcnow()
            db.add(sendlog)
            db.commit()

            # Send via email
            if sendlog.channel == "email" and recipient and recipient.email:
                status, resp = send_email_sendgrid(
                    recipient.email,
                    campaign.subject or "",
                    campaign.body or ""
                )
                if 200 <= status < 300:
                    sendlog.status = "success"
                    db.add(sendlog)
                    db.commit()
                    print(f"[send_to_recipient] Email sent successfully to {recipient.email}")
                    return {"ok": True}
                raise Exception(f"SendGrid error {status}: {resp}")

            # Send via SMS
            elif sendlog.channel == "sms" and recipient and recipient.phone:
                send_sms_twilio(recipient.phone, campaign.body or "")
                sendlog.status = "success"
                db.add(sendlog)
                db.commit()
                print(f"[send_to_recipient] SMS sent successfully to {recipient.phone}")
                return {"ok": True}

            # Invalid recipient/contact
            else:
                sendlog.status = "failed"
                sendlog.error = "Missing recipient contact or invalid channel"
                db.add(sendlog)
                db.commit()
                print(f"[send_to_recipient] Failed: {sendlog.error}")
                return {"ok": False, "error": sendlog.error}

    except Exception as exc:
        try:
            print(f"[send_to_recipient] Exception occurred: {exc}. Retrying...")
            raise self.retry(exc=exc)
        except self.MaxRetriesExceededError:
            # Use a fresh session to safely update SendLog after retries exhausted
            with SessionLocal() as db:
                sendlog = db.get(SendLog, sendlog_id)
                if sendlog:
                    sendlog.status = "failed"
                    sendlog.error = str(exc)
                    db.add(sendlog)
                    db.commit()
                    print(f"[send_to_recipient] Max retries exceeded. Marked as failed.")
            return {"ok": False, "error": str(exc)}
