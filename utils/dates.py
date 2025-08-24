import re, datetime as dt
from config import TIMEZONE

def la_today():
    try:
        from zoneinfo import ZoneInfo
        return dt.datetime.now(ZoneInfo(TIMEZONE)).date()
    except Exception:
        return dt.date.today()

def normalize_sheet_date(cell):
    if cell is None:
        return None
    s = str(cell).strip()
    if not s:
        return None

    # ISO loose: YYYY-M-D
    m = re.match(r"^(\d{4})-(\d{1,2})-(\d{1,2})$", s)
    if m:
        y, mo, d = map(int, m.groups())
        try: return dt.date(y, mo, d).isoformat()
        except: pass

    # M/D/YYYY or MM/DD/YY
    m = re.match(r"^(\d{1,2})/(\d{1,2})/(\d{2,4})$", s)
    if m:
        mo, d, y = m.groups()
        mo, d, y = int(mo), int(d), int(y)
        if y < 100: y += 2000
        try: return dt.date(y, mo, d).isoformat()
        except: pass

    # Month name: Aug 23, 2025 / August 23 2025
    m = re.match(r"^([A-Za-z]+)\s+(\d{1,2})(?:,?\s*(\d{4}))?$", s)
    if m:
        mon_str, d, y = m.groups()
        months = {"jan":1,"feb":2,"mar":3,"apr":4,"may":5,"jun":6,
                  "jul":7,"aug":8,"sep":9,"oct":10,"nov":11,"dec":12}
        mo = months.get(mon_str[:3].lower())
        if mo:
            d = int(d)
            y = int(y) if y else dt.date.today().year
            try: return dt.date(y, mo, d).isoformat()
            except: pass

    # Excel/Sheets serial
    if s.isdigit():
        try:
            serial = int(s)
            base = dt.date(1899, 12, 30)
            return (base + dt.timedelta(days=serial)).isoformat()
        except: pass
    return None

def row_date_iso(row):
    # Try 'date' col first (B)
    if len(row) > 1 and row[1]:
        iso = normalize_sheet_date(row[1])
        if iso: return iso
    # Fallback to LA day derived from timestamp_utc (A)
    if len(row) > 0 and row[0]:
        ts = str(row[0]).strip()
        try:
            if ts.endswith("Z"):
                dt_utc = dt.datetime.fromisoformat(ts.replace("Z", "+00:00"))
            else:
                dt_utc = dt.datetime.fromisoformat(ts)
                if dt_utc.tzinfo is None:
                    dt_utc = dt_utc.replace(tzinfo=dt.timezone.utc)
            try:
                from zoneinfo import ZoneInfo
                la_dt = dt_utc.astimezone(ZoneInfo(TIMEZONE))
            except Exception:
                la_dt = dt_utc - dt.timedelta(hours=8)
            return la_dt.date().isoformat()
        except:
            return None
    return None

def last_n_days_dates(n, end_date):
    return [(end_date - dt.timedelta(days=i)).isoformat() for i in range(n)]

def available_dates(rows):
    ds = {row_date_iso(r) for r in rows}
    ds.discard(None)
    return sorted(ds)
