# send_helpers.py
import os
import requests
from twilio.rest import Client

SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
FROM_EMAIL = os.getenv("SENDGRID_FROM_EMAIL")

TW_ACCOUNT = os.getenv("TWILIO_ACCOUNT_SID")
TW_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TW_FROM = os.getenv("TWILIO_FROM_NUMBER")

SENDGRID_URL = "https://api.sendgrid.com/v3/mail/send"

def send_email_sendgrid(to_email, subject, html_content, plain_text=None):
    if not SENDGRID_API_KEY or not FROM_EMAIL:
        raise RuntimeError("SendGrid not configured (API key or from email missing)")

    headers = {
        "Authorization": f"Bearer {SENDGRID_API_KEY}",
        "Content-Type": "application/json",
    }

    data = {
        "personalizations": [{"to": [{"email": to_email}], "subject": subject}],
        "from": {"email": FROM_EMAIL},
        "content": [],
    }

    if plain_text:
        data["content"].append({"type": "text/plain", "value": plain_text})
    data["content"].append({"type": "text/html", "value": html_content})

    resp = requests.post(SENDGRID_URL, json=data, headers=headers, timeout=20)
    return resp.status_code, resp.text

def send_sms_twilio(to_number, message):
    if not (TW_ACCOUNT and TW_TOKEN and TW_FROM):
        raise RuntimeError("Twilio not configured (sid/token/from missing)")
    client = Client(TW_ACCOUNT, TW_TOKEN)
    msg = client.messages.create(body=message, from_=TW_FROM, to=to_number)
    return msg.sid
