from flask import Blueprint, request, jsonify
from services.llm import extract_with_llm
from services.sheets import get_values_client, read_all_rows
from utils.dates import la_today, row_date_iso
from config import SHEET_ID

bp = Blueprint("debug", __name__)

@bp.get("/health")
def health():
    return "ok", 200

@bp.get("/routes")
def list_routes():
    # Light introspection
    from flask import current_app
    return "\n".join(sorted(rule.rule for rule in current_app.url_map.iter_rules())), 200, {"Content-Type":"text/plain"}

@bp.get("/debug-llm")
def debug_llm():
    payload = request.args.get("q", "Paid 200$ rent to Alight yesterday")
    try:
        data = extract_with_llm(payload)
        return jsonify(data), 200
    except Exception as e:
        return f"LLM failed: {e}", 500

@bp.get("/debug-sheets")
def debug_sheets():
    try:
        client = get_values_client()
        res = client.get(spreadsheetId=SHEET_ID, range="transactions!A:I").execute()
        count = max(0, len(res.get("values", [])) - 1)
        return f"Sheets OK. Rows={count}", 200
    except Exception as e:
        return f"Sheets failed: {e}", 500

@bp.get("/debug-summary-data")
def debug_summary_data():
    rows = read_all_rows()
    today = la_today().isoformat()
    parsed = []
    for i, r in enumerate(rows[:20]):
        parsed.append({"i": i, "raw": r, "parsed_date": row_date_iso(r),
                       "amount": r[3] if len(r) > 3 else None,
                       "category": r[5] if len(r) > 5 else None})
    todays = [r for r in rows if row_date_iso(r) == today]
    return jsonify({"row_count": len(rows), "today_LA": today,
                    "todays_count": len(todays), "first_rows": parsed}), 200
