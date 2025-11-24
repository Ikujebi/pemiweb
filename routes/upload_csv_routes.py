from flask import request, jsonify
from models import SessionLocal, Recipient, Campaign, SendLog
from utils import parse_csv_file, validate_email_address, validate_phone_number
from tasks import send_to_recipient

def register_upload_csv_routes(app):
    @app.route("/upload_csv", methods=["POST"])
    def upload_csv():
        file = request.files.get("file")
        name = request.form.get("name", "Daily Campaign")
        subject = request.form.get("subject", "")
        default_region = request.form.get("default_region", None)

        if not file:
            return jsonify({"error": "file required"}), 400

        rows = parse_csv_file(file.stream)
        db = SessionLocal()
        campaign = Campaign(name=name, subject=subject, body=request.form.get("body", ""))
        db.add(campaign)
        db.commit()
        db.refresh(campaign)

        added = 0
        queued = 0
        seen = set()

        for r in rows:
            raw_email = r.get("email") or ""
            raw_phone = r.get("phone") or r.get("number") or ""
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
