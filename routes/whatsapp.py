from flask import Blueprint, request, Response
from twilio.twiml.messaging_response import MessagingResponse

from services.llm import extract_with_llm
from services.ocr import ocr_from_media_url
from services.sheets import append_transaction_row
from utils.dates import la_today

bp = Blueprint("whatsapp", __name__)

@bp.post("/whatsapp")
def whatsapp_webhook():
    body = (request.form.get("Body") or "").strip()
    msg_sid = request.form.get("MessageSid") or ""
    num_media = int(request.form.get("NumMedia", "0"))
    source = "image" if num_media > 0 else "text"

    try:
        if source == "text":
            data = extract_with_llm(body)
            if not data.get("date"):
                data["date"] = la_today().isoformat()
        else:
            media_url = request.form.get("MediaUrl0") or ""
            ocr_text = ocr_from_media_url(media_url) if media_url else ""
            combined = (body + "\n" + ocr_text).strip() if body else (ocr_text or "image receipt")
            data = extract_with_llm(combined)
            if not data.get("date"):
                data["date"] = la_today().isoformat()
    except Exception as e:
        resp = MessagingResponse()
        resp.message(f"LLM/OCR error: {e}")
        return Response(str(resp), mimetype="application/xml")

    # Write to Google Sheet
    try:
        append_transaction_row(data, source, msg_sid)
    except Exception as e:
        resp = MessagingResponse()
        pretty_amt = f'{data.get("currency","USD")} {data.get("amount")}' if data.get("amount") is not None else "Unknown amount"
        resp.message(f"Parsed but sheet append failed: {data.get('name','?')} · {pretty_amt} · {data.get('category','?')} · {data.get('date','?')}\n({e})")
        return Response(str(resp), mimetype="application/xml")

    resp = MessagingResponse()
    pretty_amt = f'{data["currency"]} {data["amount"]}' if data["amount"] is not None else "Unknown amount"
    resp.message(f"Logged: {data['name']} · {pretty_amt} · {data['category']} · {data['date']}")
    return Response(str(resp), mimetype="application/xml")
