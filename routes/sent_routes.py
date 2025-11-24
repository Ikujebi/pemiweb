from flask import render_template
from models import SessionLocal, SendLog, Recipient

def register_sent_routes(app):
    @app.route("/sent_messages")
    def sent_messages():
        db = SessionLocal()
        messages = db.query(SendLog).join(Recipient).all()
        db.close()
        for msg in messages:
            msg.recipient_initials = ''.join([n[0].upper() for n in (msg.recipient.email or msg.recipient.phone).split()[:2]])
        return render_template("sent_messages.html", sent_messages=messages)
