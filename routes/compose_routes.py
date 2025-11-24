from flask import request, render_template
from models import SessionLocal, Recipient, Campaign, SendLog
from utils import validate_email_address, validate_phone_number
from tasks import send_to_recipient

def register_compose_routes(app):
    @app.route("/compose", methods=["GET", "POST"])
    def compose():
        if request.method == "POST":
            recipient = request.form.get("recipient")
            subject = request.form.get("subject")
            body = request.form.get("body")
            default_region = request.form.get("default_region", None)

            if not recipient or not body:
                return "Recipient and message body are required.", 400

            db = SessionLocal()

            # Determine if recipient is email or phone
            email = validate_email_address(recipient)
            phone = validate_phone_number(recipient, default_region)

            if not email and not phone:
                return "Invalid email or phone number.", 400

            # Check if recipient exists
            existing = None
            if email:
                existing = db.query(Recipient).filter(Recipient.email == email).first()
            if not existing and phone:
                existing = db.query(Recipient).filter(Recipient.phone == phone).first()

            if existing:
                recipient_obj = existing
            else:
                recipient_obj = Recipient(email=email, phone=phone, opted_in=True)
                db.add(recipient_obj)
                db.commit()
                db.refresh(recipient_obj)

            # Create campaign
            campaign = Campaign(name=f"Single Message to {recipient}", subject=subject, body=body)
            db.add(campaign)
            db.commit()
            db.refresh(campaign)

            # Create log
            channel = "email" if email else "sms"
            log = SendLog(campaign_id=campaign.id, recipient_id=recipient_obj.id, channel=channel, status="pending")
            db.add(log)
            db.commit()
            db.refresh(log)

            # Queue sending
            send_to_recipient.apply_async(args=[log.id])
            db.close()

            return "Message queued successfully!"

        return render_template("compose.html")
