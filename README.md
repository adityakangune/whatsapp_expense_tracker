# WhatsApp Expense Tracker

Send texts/receipt photos to WhatsApp → extract details (LLM + OCR) → log to Google Sheets → get daily/weekly/monthly summaries back on WhatsApp.

## What it does
- Ingests WhatsApp messages (text + images) via Twilio webhook.
- OCR for images (defaults to OCR.Space; no Tesseract needed on Cloud Run).
- LLM parses messages into: **name, amount, category, date**.
- Writes rows to **Google Sheets**.
- Scheduled summaries (daily/weekly/monthly) via Cloud Scheduler hitting protected endpoints.

## Stack
- **Flask + Gunicorn** on **Cloud Run**
- **Google Sheets API** (service account)
- **Twilio WhatsApp Sandbox**
- **OCR.Space** (free OCR tier)
- **Groq (Llama 3.1)** for parsing & summaries

## Environment variables
Copy `.env.example` to your own env or set these as Cloud Run service env vars:

- `TIMEZONE` (e.g., `America/Los_Angeles`)
- `SHEET_ID`
- `GROQ_API_KEY`
- `OCR_BACKEND` (default: `ocrspace`)
- `OCRSPACE_API_KEY`
- `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`
- `TWILIO_WHATSAPP_FROM`, `YOUR_WHATSAPP_NUMBER`
- `INTERNAL_CRON_TOKEN` (random hex used to protect summary endpoints)

## Local dev (optional)
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
# export your env vars or `cp .env.example .env` then export from it
python app.py
```

## Cloud Run deploy (manual)
```bash
PROJECT_ID=your-project-id
SERVICE=expense-tracker
REGION=us-central1

gcloud builds submit --tag gcr.io/$PROJECT_ID/$SERVICE
gcloud run deploy $SERVICE --image gcr.io/$PROJECT_ID/$SERVICE   --region $REGION --allow-unauthenticated --port 8080
```

## Webhook
In **Twilio Console → WhatsApp Sandbox**, set **When a message comes in** to:
```
https://<your-cloud-run-url>/whatsapp
```

## Scheduler (examples)
Create daily/weekly/monthly jobs calling these endpoints with your `INTERNAL_CRON_TOKEN`:
```
/daily-summary-ai?token=... 
/weekly-summary-ai?token=...
/monthly-summary-ai?token=...
```

## Notes
- Twilio sandbox requires you to have messaged the bot within the last **24 hours** for non-template outbound messages.
- Share your Google Sheet with the Cloud Run service account (Editor).
- Keep secrets out of git. See `.gitignore` and `.gcloudignore` provided here.
