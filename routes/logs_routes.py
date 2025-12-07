# routes/logs_routes.py
from flask import render_template, request
from database import SessionLocal
from models import SendLog, Recipient, Campaign
from sqlalchemy.orm import joinedload

def register_logs_routes(app):
    @app.route("/logs")
    def logs():
        page = request.args.get("page", 1, type=int)  # optional pagination
        per_page = 50

        with SessionLocal() as db:
            query = db.query(SendLog).options(
                joinedload(SendLog.recipient),
                joinedload(SendLog.campaign)
            ).order_by(SendLog.created_at.desc())  # latest logs first

            # Simple pagination
            logs_list = query.offset((page - 1) * per_page).limit(per_page).all()

            for log in logs_list:
                # safely handle missing recipient info
                contact = (log.recipient.email or log.recipient.phone or "")
                log.recipient_initials = ''.join([n[0].upper() for n in contact.split()[:2]]) if contact else "NA"

        return render_template("logs.html", logs=logs_list, page=page)
