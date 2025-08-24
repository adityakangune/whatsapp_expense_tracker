import os
from dotenv import load_dotenv
load_dotenv()

# Core / time
TIMEZONE = os.getenv("TIMEZONE", "America/Los_Angeles")

# Google Sheets
SHEET_ID = os.getenv("SHEET_ID")  # required
SERVICE_ACCOUNT_JSON = os.getenv("SERVICE_ACCOUNT_JSON", "service_account.json")
SERVICE_ACCOUNT_JSON_CONTENT = os.getenv("SERVICE_ACCOUNT_JSON_CONTENT")  # inline JSON optional

# LLM (Groq / Grok)
GROQ_API_KEY = os.getenv("GROQ_API_KEY")  # required

# OCR
OCR_BACKEND = os.getenv("OCR_BACKEND", "ocrspace")  # ocrspace | tesseract
OCRSPACE_API_KEY = os.getenv("OCRSPACE_API_KEY")    # required if ocrspace
TESSERACT_CMD = os.getenv("TESSERACT_CMD", r"C:\Program Files\Tesseract-OCR\tesseract.exe")

# Twilio WhatsApp
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")      # required
TWILIO_AUTH_TOKEN  = os.getenv("TWILIO_AUTH_TOKEN")       # required
TWILIO_WHATSAPP_FROM = os.getenv("TWILIO_WHATSAPP_FROM")  # e.g., whatsapp:+14155238886
YOUR_WHATSAPP_NUMBER = os.getenv("YOUR_WHATSAPP_NUMBER")  # e.g., whatsapp:+1XXXXXXXXXX

# Optional: protect cron endpoints (add ?token=... to your scheduler call)
INTERNAL_CRON_TOKEN = os.getenv("INTERNAL_CRON_TOKEN")
