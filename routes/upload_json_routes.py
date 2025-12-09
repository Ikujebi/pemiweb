# routes/upload_json_routes.py
from flask import request, jsonify
from database import SessionLocal
from models import Recipient, Campaign, SendLog
from utils import validate_email_address, validate_phone_number
from tasks import send_to_recipient
import traceback

def register_upload_json_routes(app):
    @app.route("/upload_json", methods=["POST"])
    def upload_json():
        log_id = None
        channel = None
        recipient_id = None   # store primitive value

        with SessionLocal() as db:
            try:
                recipient_raw = request.form.get("recipient", "").strip()
                subject = request.form.get("subject", "").strip()
                body = request.form.get("body", "").strip()
                default_region = request.form.get("default_region", None)

                email = validate_email_address(recipient_raw) or None
                phone = validate_phone_number(recipient_raw, default_region) or None

                if not email and not phone:
                    return jsonify({"sent": False, "error": "Recipient must be a valid email or phone"}), 400

                campaign = Campaign(name="Single Message", subject=subject, body=body)
                db.add(campaign)
                db.commit()
                db.refresh(campaign)

                recipient = None
                if email:
                    recipient = db.query(Recipient).filter_by(email=email).first()
                if not recipient and phone:
                    recipient = db.query(Recipient).filter_by(phone=phone).first()

                if not recipient:
                    recipient = Recipient(email=email, phone=phone)
                    db.add(recipient)
                    db.commit()
                    db.refresh(recipient)

                recipient_id = recipient.id  # extract ID before session closes

                channel = "email" if email else "sms"

                log = SendLog(
                    campaign_id=campaign.id,
                    recipient_id=recipient_id,
                    channel=channel,
                    status="pending"
                )
                db.add(log)
                db.commit()
                db.refresh(log)

                log_id = log.id

            except Exception as e:
                traceback.print_exc()
                return jsonify({"sent": False, "error": str(e)}), 500

        # Call Celery task AFTER session closes
        send_to_recipient.apply_async(args=[log_id])

        return jsonify({
            "sent": True,
            "recipient_id": recipient_id,
            "channel": channel
        }), 200
