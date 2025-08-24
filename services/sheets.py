import os, json
import datetime as dt
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from config import SERVICE_ACCOUNT_JSON, SERVICE_ACCOUNT_JSON_CONTENT, SHEET_ID

_sheets_values = None

def _load_sa_info():
    if SERVICE_ACCOUNT_JSON_CONTENT:
        return json.loads(SERVICE_ACCOUNT_JSON_CONTENT)
    with open(SERVICE_ACCOUNT_JSON) as f:
        return json.load(f)

def get_values_client():
    global _sheets_values
    if _sheets_values:
        return _sheets_values
    sa_info = _load_sa_info()
    creds = Credentials.from_service_account_info(
        sa_info, scopes=["https://www.googleapis.com/auth/spreadsheets"]
    )
    _sheets_values = build("sheets", "v4", credentials=creds).spreadsheets().values()
    print("Google Sheets client initialized.")
    return _sheets_values

def append_transaction_row(data: dict, source: str, msg_sid: str):
    ts = dt.datetime.utcnow().isoformat()
    row = [
        ts,
        data.get("date"),
        data.get("name"),
        data.get("amount"),
        data.get("currency"),
        data.get("category"),
        data.get("notes"),
        source,
        msg_sid
    ]
    client = get_values_client()
    client.append(
        spreadsheetId=SHEET_ID,
        range="transactions!A:I",
        valueInputOption="USER_ENTERED",
        body={"values": [row]}
    ).execute()

def read_all_rows():
    client = get_values_client()
    res = client.get(spreadsheetId=SHEET_ID, range="transactions!A:I").execute()
    return res.get("values", [])[1:]
