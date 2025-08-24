import requests
from config import TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_WHATSAPP_FROM, YOUR_WHATSAPP_NUMBER

def send_whatsapp(body: str):
    if not all([TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_WHATSAPP_FROM, YOUR_WHATSAPP_NUMBER]):
        raise RuntimeError("Missing Twilio env vars")
    r = requests.post(
        f"https://api.twilio.com/2010-04-01/Accounts/{TWILIO_ACCOUNT_SID}/Messages.json",
        auth=(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN),
        data={"From": TWILIO_WHATSAPP_FROM, "To": YOUR_WHATSAPP_NUMBER, "Body": body},
        timeout=20
    )
    r.raise_for_status()
    return True
