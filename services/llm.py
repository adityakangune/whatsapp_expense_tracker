import json, re
from groq import Groq
from config import GROQ_API_KEY

groq_client = Groq(api_key=GROQ_API_KEY)

SYSTEM_PROMPT = (
    "You are a strict JSON generator. Always respond with a single JSON object and nothing else.\n"
    "Task: extract expense data from a short message.\n"
    "Return a JSON object with keys:\n"
    "- name: merchant or person (string)\n"
    "- amount: number only, no currency symbol, null if missing\n"
    "- currency: 3-letter code, default USD if unclear\n"
    "- category: one of [rent, groceries, eating_out, utilities, transport, shopping, medical, entertainment, travel, education, transfer, other]\n"
    "- date: YYYY-MM-DD in America/Los_Angeles, use today in that timezone if not present\n"
    "- notes: short summary\n"
    "Output must be valid JSON."
)

def extract_with_llm(text: str) -> dict:
    r = groq_client.chat.completions.create(
        model="llama-3.1-8b-instant",
        response_format={"type": "json_object"},  # Groq JSON mode needs 'json' mention in messages, done below
        temperature=0,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Return JSON only. Input: {text.strip()}"}
        ],
    )
    data = json.loads(r.choices[0].message.content)

    # normalize
    amt = data.get("amount", None)
    try:
        data["amount"] = float(amt) if amt is not None else None
    except Exception:
        data["amount"] = None

    data["currency"] = data.get("currency") or "USD"
    data["category"] = data.get("category") or "other"
    data["name"] = data.get("name") or "Unknown"
    data["notes"] = data.get("notes") or text.strip()

    # date format guard
    date_str = data.get("date", "")
    if not re.match(r"^\d{4}-\d{2}-\d{2}$", date_str or ""):
        data["date"] = None  # routes layer sets LA "today" if missing
    return data

# ---- AI summaries
FIN_ASST_SYSTEM = (
    "You are a helpful financial assistant named Grok. "
    "Write concise, WhatsApp-friendly text. No markdown links."
)

def grok_summarize(context: dict) -> str:
    msg = (
        "Return plain text (not JSON). "
        "Here is the expense data in JSON:\n\n"
        + json.dumps(context, ensure_ascii=False)
        + "\n\nNow write the summary and advice."
    )
    r = groq_client.chat.completions.create(
        model="llama-3.1-8b-instant",
        temperature=0.4,
        messages=[
            {"role": "system", "content": FIN_ASST_SYSTEM},
            {"role": "user", "content": msg}
        ],
    )
    return r.choices[0].message.content.strip()

def grok_summarize_window(ctx: dict) -> str:
    msg = (
        "Return plain text (not JSON). "
        "Here is the expense data in JSON for the window and previous window:\n\n"
        + json.dumps(ctx, ensure_ascii=False)
        + "\n\nNow write the summary and advice."
    )
    r = groq_client.chat.completions.create(
        model="llama-3.1-8b-instant",
        temperature=0.4,
        messages=[
            {"role": "system", "content": FIN_ASST_SYSTEM},
            {"role": "user", "content": msg}
        ],
    )
    return r.choices[0].message.content.strip()
