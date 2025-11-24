from flask import request, jsonify
from models import SessionLocal, Recipient, Campaign, SendLog
from utils import validate_email_address, validate_phone_number
from tasks import send_to_recipient

def register_upload_json_routes(app):
    @app.route("/upload_json", methods=["POST"])
    def upload_json():
        data = request.get_json() or {}
        recs = data.get("recipients", [])
        name = data.get("campaign", {}).get("name", "Daily Campaign")
        subject = data.get("campaign", {}).get("subject", "")
        body = data.get("campaign", {}).get("body", "")
        default_region = data.get("default_region", None)

        db = SessionLocal()
        campaign = Campaign(name=name, subject=subject, body=body)
        db.add(campaign)
        db.commit()
        db.refresh(campaign)

        added = 0
        queued = 0
        seen = set()

        for r in recs:
            raw_email = r.get("email", "") or ""
            raw_phone = r.get("phone", "") or ""
            email = validate_email_address(raw_email) or None
            phone = validate_phone_number(raw_phone, default_region) or None
            if not email and not phone:
                continue

            key = f"{email or ''}|{phone or ''}"
            if key in seen:
                continue
            seen.add(key)

            existing = None
            if email:
                existing = db.query(Recipient).filter(Recipient.email == email).first()
            if not existing and phone:
                existing = db.query(Recipient).filter(Recipient.phone == phone).first()

            if existing:
                recipient = existing
            else:
                recipient = Recipient(email=email, phone=phone, opted_in=True)
                db.add(recipient)
                db.commit()
                db.refresh(recipient)
                added += 1

            channel = "email" if email else "sms"
            log = SendLog(campaign_id=campaign.id, recipient_id=recipient.id, channel=channel, status="pending")
            db.add(log)
            db.commit()
            db.refresh(log)
            send_to_recipient.apply_async(args=[log.id])
            queued += 1

        db.close()
        return jsonify({"added": added, "queued": queued}), 200
