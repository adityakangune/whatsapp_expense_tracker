from flask import Blueprint, request
import datetime as dt
import calendar

from services.sheets import read_all_rows
from services.messaging import send_whatsapp
from services.llm import grok_summarize, grok_summarize_window
from utils.dates import la_today, row_date_iso, last_n_days_dates, available_dates
from config import INTERNAL_CRON_TOKEN

bp = Blueprint("summary", __name__)

def _safe_float(x):
    try: return float(x)
    except: return 0.0

def _aggregate(rows):
    by_cat, by_name = {}, {}
    total, n = 0.0, 0
    for r in rows:
        if len(r) < 6: 
            continue
        amt = _safe_float(r[3]) if len(r) > 3 else 0.0
        name = r[2] if len(r) > 2 and r[2] else "Unknown"
        cat  = r[5] if len(r) > 5 and r[5] else "other"
        total += amt; n += 1
        by_cat[cat] = by_cat.get(cat, 0.0) + amt
        by_name[name] = by_name.get(name, 0.0) + amt
    top_cat = max(by_cat.items(), key=lambda kv: kv[1])[0] if by_cat else None
    top_name = max(by_name.items(), key=lambda kv: kv[1])[0] if by_name else None
    return {"total": round(total,2), "count": n, "by_category": by_cat, "by_merchant": by_name,
            "top_category": top_cat, "top_merchant": top_name}

def _slice_rows_by_date(rows, yyyy_mm_dd):
    return [r for r in rows if row_date_iso(r) == yyyy_mm_dd]

def build_daily_context(target_date=None, days_window=7, fallback_to_latest=True):
    rows = read_all_rows()
    today_iso = la_today().isoformat()
    date_to_use = target_date or today_iso
    todays_rows = _slice_rows_by_date(rows, date_to_use)
    if not todays_rows and fallback_to_latest:
        ds = available_dates(rows)
        if ds:
            date_to_use = ds[-1]
            todays_rows = _slice_rows_by_date(rows, date_to_use)
    today_metrics = _aggregate(todays_rows)

    end_date = dt.date.fromisoformat(date_to_use)
    datesN = set(last_n_days_dates(days_window, end_date))
    rowsN = [r for r in rows if (row_date_iso(r) in datesN)]
    mN = _aggregate(rowsN)

    uniq = {row_date_iso(r) for r in rowsN}; uniq.discard(None)
    avg_per_day = round(mN["total"]/max(1,len(uniq)), 2) if uniq else 0.0

    return {"date_used": date_to_use, "today": today_metrics,
            "last_window_days": days_window,
            "last_window": {"total": mN["total"], "count": mN["count"], "avg_per_day": avg_per_day, "by_category": mN["by_category"]}}

def _cron_guard():
    if not INTERNAL_CRON_TOKEN:
        return None  # no guard configured
    token = request.args.get("token")
    if token != INTERNAL_CRON_TOKEN:
        return ("Unauthorized", 401, {"Content-Type":"text/plain"})
    return None

# -------- Daily
@bp.get("/daily-summary-ai-preview")
def daily_summary_ai_preview():
    ctx = build_daily_context(request.args.get("date"))
    if ctx["today"]["count"] == 0:
        return f"Daily summary for {ctx['date_used']}\nNo expenses logged.", 200, {"Content-Type": "text/plain; charset=utf-8"}
    return grok_summarize(ctx), 200, {"Content-Type": "text/plain; charset=utf-8"}

@bp.get("/daily-summary-ai")
def daily_summary_ai():
    guard = _cron_guard()
    if guard: return guard
    ctx = build_daily_context(request.args.get("date"))
    body = f"Daily summary for {ctx['date_used']}\nNo expenses logged." if ctx["today"]["count"] == 0 else grok_summarize(ctx)
    send_whatsapp(body)
    return {"ok": True, "sent": body, "date_used": ctx["date_used"]}, 200

# -------- Week helpers
def week_bounds(anchor_date: dt.date):
    start = anchor_date - dt.timedelta(days=anchor_date.weekday())
    end = start + dt.timedelta(days=6)
    return start.isoformat(), end.isoformat()

def month_bounds(anchor_date: dt.date):
    y, m = anchor_date.year, anchor_date.month
    first = dt.date(y, m, 1)
    last = dt.date(y, m, calendar.monthrange(y, m)[1])
    return first.isoformat(), last.isoformat()

def _dates_between_inclusive(start_iso, end_iso):
    s, e = dt.date.fromisoformat(start_iso), dt.date.fromisoformat(end_iso)
    return [(s + dt.timedelta(days=i)).isoformat() for i in range((e - s).days + 1)]

def _aggregate_window(rows, start_iso, end_iso):
    days = set(_dates_between_inclusive(start_iso, end_iso))
    rows_window = [r for r in rows if (row_date_iso(r) in days)]
    return _aggregate(rows_window), rows_window

def prev_week_bounds(week_start_iso):
    start = dt.date.fromisoformat(week_start_iso)
    prev_end = start - dt.timedelta(days=1)
    prev_start = prev_end - dt.timedelta(days=6)
    return prev_start.isoformat(), prev_end.isoformat()

def prev_month_bounds(month_start_iso):
    start = dt.date.fromisoformat(month_start_iso)
    y, m = start.year, start.month
    py, pm = (y-1, 12) if m == 1 else (y, m-1)
    first = dt.date(py, pm, 1)
    last = dt.date(py, pm, calendar.monthrange(py, pm)[1])
    return first.isoformat(), last.isoformat()

def build_window_context(label, start_iso, end_iso, compare_prev=True):
    rows = read_all_rows()
    metrics, rows_window = _aggregate_window(rows, start_iso, end_iso)
    prev = None
    if compare_prev:
        if label == "week":
            ps, pe = prev_week_bounds(start_iso)
        else:
            ps, pe = prev_month_bounds(start_iso)
        prev_metrics, _ = _aggregate_window(rows, ps, pe)
        prev = {"start": ps, "end": pe, "metrics": prev_metrics}
    uniq = {row_date_iso(r) for r in rows_window}; uniq.discard(None)
    avg_per_day = round(metrics["total"]/max(1,len(uniq)), 2) if uniq else 0.0
    return {"label": label, "window": {"start": start_iso, "end": end_iso, "metrics": metrics, "avg_per_day": avg_per_day}, "previous_window": prev}

# -------- Weekly
@bp.get("/weekly-summary-ai-preview")
def weekly_summary_ai_preview():
    q_date = request.args.get("date")
    rows = read_all_rows()
    anchors = available_dates(rows)
    anchor = dt.date.fromisoformat(q_date) if q_date else (dt.date.fromisoformat(anchors[-1]) if anchors else la_today())
    start_iso, end_iso = week_bounds(anchor)
    ctx = build_window_context("week", start_iso, end_iso, compare_prev=True)
    text = grok_summarize_window(ctx) if ctx["window"]["metrics"]["count"] > 0 else f"Weekly summary {start_iso} → {end_iso}\nNo expenses logged."
    return f"[week used: {start_iso} → {end_iso}]\n{text}", 200, {"Content-Type": "text/plain; charset=utf-8"}

@bp.get("/weekly-summary-ai")
def weekly_summary_ai():
    guard = _cron_guard()
    if guard: return guard
    q_date = request.args.get("date")
    rows = read_all_rows()
    anchors = available_dates(rows)
    anchor = dt.date.fromisoformat(q_date) if q_date else (dt.date.fromisoformat(anchors[-1]) if anchors else la_today())
    start_iso, end_iso = week_bounds(anchor)
    ctx = build_window_context("week", start_iso, end_iso, compare_prev=True)
    body = grok_summarize_window(ctx) if ctx["window"]["metrics"]["count"] > 0 else f"Weekly summary {start_iso} → {end_iso}\nNo expenses logged."
    send_whatsapp(body)
    return {"ok": True, "sent": body, "week": [start_iso, end_iso]}, 200

# -------- Monthly
@bp.get("/monthly-summary-ai-preview")
def monthly_summary_ai_preview():
    q_date = request.args.get("date")
    rows = read_all_rows()
    anchors = available_dates(rows)
    anchor = dt.date.fromisoformat(q_date) if q_date else (dt.date.fromisoformat(anchors[-1]) if anchors else la_today())
    start_iso, end_iso = month_bounds(anchor)
    ctx = build_window_context("month", start_iso, end_iso, compare_prev=True)
    text = grok_summarize_window(ctx) if ctx["window"]["metrics"]["count"] > 0 else f"Monthly summary {start_iso[:7]}\nNo expenses logged."
    return f"[month used: {start_iso} → {end_iso}]\n{text}", 200, {"Content-Type": "text/plain; charset=utf-8"}

@bp.get("/monthly-summary-ai")
def monthly_summary_ai():
    guard = _cron_guard()
    if guard: return guard
    q_date = request.args.get("date")
    rows = read_all_rows()
    anchors = available_dates(rows)
    anchor = dt.date.fromisoformat(q_date) if q_date else (dt.date.fromisoformat(anchors[-1]) if anchors else la_today())
    start_iso, end_iso = month_bounds(anchor)
    ctx = build_window_context("month", start_iso, end_iso, compare_prev=True)
    body = grok_summarize_window(ctx) if ctx["window"]["metrics"]["count"] > 0 else f"Monthly summary {start_iso[:7]}\nNo expenses logged."
    send_whatsapp(body)
    return {"ok": True, "sent": body, "month": [start_iso, end_iso]}, 200
