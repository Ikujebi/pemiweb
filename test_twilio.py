from twilio.rest import Client
import os

TW_ACCOUNT = os.getenv("TWILIO_ACCOUNT_SID")
TW_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TW_FROM = os.getenv("TWILIO_FROM_NUMBER")

client = Client(TW_ACCOUNT, TW_TOKEN)

# Try fetching account info instead of sending SMS
try:
    account = client.api.accounts(TW_ACCOUNT).fetch()
    print("Authenticated! Account name:", account.friendly_name)
except Exception as e:
    print("Authentication failed:", e)